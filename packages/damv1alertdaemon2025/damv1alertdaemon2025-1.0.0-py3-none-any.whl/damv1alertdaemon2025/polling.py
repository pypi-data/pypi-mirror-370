# polling.py
import requests
import time
import json
from datetime import datetime, timedelta
import pytz
import hashlib

from .match_engine import should_alert
from .grafana_url_generator import generate_grafana_explore_url
from .discord_sender import is_content_suspicious, send_discord_alert, send_discord_bundle_messages, send_discord_bundle_messages_eco
from .state_manager import (
    generate_alert_id,
    load_polling_state,
    save_polling_state,
    reset_polling_state,
    cleanup_old_polling_states
)

RESTART_INFO_PATH = "./temp/last_restart_info.json"
TIMESTAMP_STORE = "last_timestamps.json"
CLEANUP_OLD_ENTRIES_SECONDS = 24 * 60 * 60 # 24 jam
DELAY_BUFFER_SECONDS = 2
DEFAULT_OFFSET_START = 3
DEFAULT_OFFSET_END = 3
THREAD_MONITOR_INTERVAL = 60

PROCESSED_IDS_WINDOW_SECONDS = 10 # Bisa disesuaikan

last_log_time = {}

## -- [ Initialize ] ---------------------------------------------------------------
def get_default_config():
    return {
        # Path & penyimpanan
        "RESTART_INFO_PATH": RESTART_INFO_PATH,
        "TIMESTAMP_STORE": TIMESTAMP_STORE,

        # Waktu cleanup
        "CLEANUP_OLD_ENTRIES_SECONDS": CLEANUP_OLD_ENTRIES_SECONDS,
        
        # Polling defaults
        "DELAY_BUFFER_SECONDS": DELAY_BUFFER_SECONDS,
        "DEFAULT_OFFSET_START": DEFAULT_OFFSET_START,
        "DEFAULT_OFFSET_END": DEFAULT_OFFSET_END,
        "PROCESSED_IDS_WINDOW_SECONDS": PROCESSED_IDS_WINDOW_SECONDS,

        # Nilai dari load_alert_config()
        "ALERT_CONFIGS": [],
        "DEFAULT_OFFSET": {},
        "DEFAULT_BUNDLE_MODE": "split",
        "ECO_CONFIG": {},

        "THREAD_MONITOR_INTERVAL": THREAD_MONITOR_INTERVAL,
    }

## -- [ 001 ] ----------------------------------------------------------------------
def is_eco_mode_active(now: datetime, eco_config: dict) -> bool:
    if not eco_config.get("enabled", False):
        return False

    tz = pytz.timezone(eco_config.get("timezone", "Asia/Jakarta"))
    now = now.astimezone(tz)
    start = eco_config.get("start_hour", 0)
    end = eco_config.get("end_hour", 0)

    if start == end:
        return False  # Tidak ada rentang waktu

    if start < end:
        # Rentang normal (misal: 17 - 21)
        return start <= now.hour < end
    else:
        # Rentang menyilang hari (misal: 21 - 0)
        return now.hour >= start or now.hour < end

## -- [ 002 ] ----------------------------------------------------------------------
def check_loki_ready(loki_url):
    try:
        response = requests.get(f"{loki_url}/ready", timeout=5)
        if response.status_code == 200:
            print(f"[INFO] Loki status: READY ({loki_url}/ready)")
            return True
        else:
            print(f"[WARNING] Loki status: NOT READY ({response.status_code}) - {loki_url}/ready")
            return False
    except Exception as e:
        print(f"[ERROR] Gagal mengakses Loki: {e}")
        return False

## -- [ 003 ] ----------------------------------------------------------------------
def now_jakarta():
    tz = pytz.timezone("Asia/Jakarta")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

## -- [ 004 ] ----------------------------------------------------------------------
def load_last_timestamps(config):
    timestamp_store = config.get("TIMESTAMP_STORE")
    cleanup_old_entries_seconds = config.get("CLEANUP_OLD_ENTRIES_SECONDS")

    try:
        with open(timestamp_store) as f:
            data = json.load(f)

        now_ns = int(time.time() * 1e9)
        cutoff_ns = now_ns - (cleanup_old_entries_seconds * 1e9)

        cleaned_data = {}
        removed_count = 0
        for key, state in data.items():
            if isinstance(state, dict):
                last_ts = state.get("last_ts")
                if last_ts and last_ts > cutoff_ns:
                    cleaned_data[key] = state
                elif last_ts and last_ts <= cutoff_ns:
                    removed_count += 1
            else:
                ts_int = int(state) if isinstance(state, (int, float)) else 0
                if ts_int > cutoff_ns:
                    cleaned_data[key] = {
                        "last_ts": ts_int,
                        "processed_entries": []
                    }
                else:
                    removed_count += 1

        if removed_count > 0:
            print(f"[INFO] Cleanup: {removed_count} entri lama dihapus dari {timestamp_store}")
            save_last_timestamps(cleaned_data, config)

        return cleaned_data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"[WARNING] File {timestamp_store} rusak. Membuat file baru. Error: {e}")
        return {}
    except Exception as e:
        print(f"[WARNING] Gagal memuat timestamp: {e}")
        return {}

## -- [ 005 ] ----------------------------------------------------------------------
def save_last_timestamps(timestamps, config):
    try:
        # Ambil konfigurasi dari config
        timestamp_store = config.get("TIMESTAMP_STORE", "last_timestamps.json")
        cleanup_old_entries_seconds = config.get("CLEANUP_OLD_ENTRIES_SECONDS")

        # Lakukan cleanup saat menyimpan
        now_ns = int(time.time() * 1e9)
        cutoff_ns = now_ns - (cleanup_old_entries_seconds * 1e9)

        cleaned_timestamps = {
            k: v for k, v in timestamps.items()
            if isinstance(v, dict) and v.get("last_ts", 0) > cutoff_ns
        }

        if len(cleaned_timestamps) < len(timestamps):
            removed_count = len(timestamps) - len(cleaned_timestamps)
            print(f"[INFO] Cleanup saat save: {removed_count} entri lama dihapus.")

        with open(timestamp_store, 'w') as f:
            json.dump(cleaned_timestamps, f)  
    except Exception as e:
        print(f"[WARNING] Gagal menyimpan timestamp: {e}")

## -- [ 006 ] ----------------------------------------------------------------------
def query_loki(config, query, start_ns, end_ns):
    loki_url = config["LOKI_URL"]
    limit = config["LIMIT"]

    try:
        resp = requests.get(f"{loki_url}/loki/api/v1/query_range", params={
            "query": query,
            "limit": limit,
            "start": int(start_ns),
            "end": int(end_ns),
            "direction": "forward"
        })
        if resp.status_code != 200:
            return {"error": resp.text}
        return resp.json().get("data", {}).get("result", [])
    except Exception as e:
        return {"error": str(e)}

## -- [ 007 ] ----------------------------------------------------------------------
def validate_single_alert(alert: dict, index: int):
    required_fields = {
        "query": str,
        "title": str,
        "category": str
    }

    optional_fields = {
        "mode": ("bundle", "single"),
        "polling_delay": int,
        "start_offset": int,
        "end_offset": int,
        "include_bundle_header": bool,
        "mentions": list,
    }

    for field, expected_type in required_fields.items():
        if field not in alert or not isinstance(alert[field], expected_type):
            raise ValueError(f"Alert ke-{index}: Field '{field}' harus bertipe {expected_type.__name__} dan wajib ada.")

    for field, expected in optional_fields.items():
        if field in alert:
            value = alert[field]
            if isinstance(expected, tuple):  # enum case
                if value not in expected:
                    raise ValueError(f"Alert ke-{index}: Field '{field}' harus salah satu dari {expected}")
            elif not isinstance(value, expected):
                raise ValueError(f"Alert ke-{index}: Field '{field}' harus bertipe {expected.__name__}")

## -- [ 008 ] ----------------------------------------------------------------------
def load_alert_config(alert_config_path):
    try:
        with open(alert_config_path) as f:
            config_structure = json.load(f)
    except Exception as e:
        print(f"[WARNING] Gagal muat konfigurasi alert: {e}")
        return [], {}, "split", {}

    if not isinstance(config_structure, dict):
        print("[WARNING] Struktur konfigurasi alert tidak valid: bukan dictionary.")
        return [], {}, "split", {}

    alerts = config_structure.get("alerts")
    if not isinstance(alerts, list):
        print("[WARNING] 'alerts' tidak ditemukan atau bukan list.")
        return [], {}, "split", {}

    valid_alerts = []
    for idx, alert in enumerate(alerts):
        try:
            validate_single_alert(alert, idx)
            valid_alerts.append(alert)
        except ValueError as ve:
            print(f"[WARNING] Alert ke-{idx} diabaikan: {ve}")

    if not valid_alerts:
        print(f"[INFO] Tidak ada alert valid di {alert_config_path}.")

    return (
        valid_alerts,
        config_structure.get("default_offset", {}),
        config_structure.get("default_bundle_mode", "split"),
        config_structure.get("eco_mode", {})
    )

## -- [ 009 ] ----------------------------------------------------------------------
def hash_log(ts_val, message):
    key = f"{ts_val}::{message.strip()}"
    return hashlib.md5(key.encode()).hexdigest()


## -- [ 010 ] ----------------------------------------------------------------------
def prune_processed_ids(processed_ids_with_ts, window_center_ns, window_size_ns):
    """
    Memfilter processed_ids untuk hanya menyimpan yang berada dalam jendela waktu tertentu.
    Args:
        processed_ids_with_ts: List of dicts [{'id': '...', 'ts': 1234567890}, ...]
        window_center_ns: Timestamp pusat jendela (biasanya last_ts) dalam nanodetik.
        window_size_ns: Ukuran jendela dalam nanodetik (PROCESSED_IDS_WINDOW_SECONDS * 1e9).
    Returns:
        List of dicts [{'id': '...', 'ts': 1234567890}, ...] yang difilter.
    """
    lower_bound = window_center_ns - window_size_ns
    upper_bound = window_center_ns + window_size_ns
    
    # Filter berdasarkan timestamp
    pruned_list = [
        entry for entry in processed_ids_with_ts
        if lower_bound <= entry['ts'] <= upper_bound
    ]
    
    # Urutkan berdasarkan timestamp (opsional, untuk konsistensi)
    pruned_list.sort(key=lambda x: x['ts'])
    
    return pruned_list


## -- [ 011 ] ----------------------------------------------------------------------
def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0:
        parts.append(f"{seconds}s")
    return "".join(parts) if parts else "0s"


def log_with_timestamp(message, context="default"):
    now = datetime.now(pytz.timezone("Asia/Jakarta"))    
    prev = last_log_time.get(context)
    # Hitung selisih
    if prev:
        delta = (now - prev).total_seconds()
        elapsed_str = f"+{format_duration(delta)}"
    else:
        elapsed_str = "start"
    last_log_time[context] = now
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[DEBUG] {message} | {timestamp_str} WIB | {elapsed_str}")




## = =[ Procedure ] = == = == = == = == = == = == = == = == = == = == = == = == = = .
def enqueue_alerts(config):
    cleanup_counter = 0
    last_data = load_last_timestamps(config)

    restart_info_path = config["RESTART_INFO_PATH"]
    delay_buffer_seconds = config["DELAY_BUFFER_SECONDS"]
    default_offset_start = config["DEFAULT_OFFSET_START"]
    default_offset_end = config["DEFAULT_OFFSET_END"]
    processed_ids_window_ns = int(config["PROCESSED_IDS_WINDOW_SECONDS"] * 1e9)
    poll_interval = config["POLL_INTERVAL"]
    limit = config["LIMIT"]
    alert_queue = config["alert_queue"]

    alert_configs = config["ALERT_CONFIGS"]
    default_offset = config["DEFAULT_OFFSET"]
    default_bundle_mode = config["DEFAULT_BUNDLE_MODE"]
    eco_config = config["ECO_CONFIG"]



    try:
        with open(restart_info_path) as f:
            restart_info = json.load(f)
            last_restart_ns = int(restart_info.get("last_restart_time_ns", int(time.time() * 1e9)))
    except Exception as e:
        print(f"[WARNING] Gagal membaca {restart_info_path}: {e}")
        last_restart_ns = int(time.time() * 1e9)

    while True:
        eco_mode_active = is_eco_mode_active(datetime.now(), eco_config)
        now_ns = int((time.time() - delay_buffer_seconds) * 1e9)
        updated_data = {}
        has_alert = False

        for cfg in alert_configs:
            query = cfg['query']
            title = cfg['title']
            category = cfg['category']
            start_offset = cfg.get("start_offset", default_offset.get("start_offset", default_offset_start))
            end_offset = cfg.get("end_offset", default_offset.get("end_offset", default_offset_end))
            polling_delay = cfg.get("polling_delay", 1)
            mode = cfg.get("mode", default_bundle_mode)
            fallback_start_ns = now_ns - (60 * 1e9)

            results = query_loki(config, query, fallback_start_ns, now_ns)
            if isinstance(results, dict) and "error" in results:
                continue

            for entry in results:
                stream = entry.get("stream", {})
                job = stream.get("job", "unknown")
                key = f"{title}::{job}"

                state = last_data.get(key, {})
                processed_entries = state.get("processed_entries", [])
                last_ts = int(state.get("last_ts", fallback_start_ns))
                processed_ids_set = {entry['id'] for entry in processed_entries}

                new_entries = []
                values = entry.get("values", [])
                log_lines = []

                for ts_val, log in values:
                    ts_int = int(ts_val)
                    if ts_int <= last_ts:
                        continue
                    if should_alert(log):
                        log_id = hash_log(ts_val, log)
                        if log_id in processed_ids_set:
                            continue

                        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                        # timestamp = datetime.fromtimestamp(int(ts_val[:10]))
                        # timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                        # #- Perbaikan 2025-08-19
                        ts_seconds = int(ts_val) / 1e9
                        utc_dt = datetime.utcfromtimestamp(ts_seconds).replace(tzinfo=pytz.utc)
                        jakarta_dt = utc_dt.astimezone(pytz.timezone('Asia/Jakarta'))
                        timestamp_str = jakarta_dt.strftime("%Y-%m-%d %H:%M:%S")
                        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                        log_entry = {
                            "timestamp_ns": ts_val,
                            "timestamp_iso": timestamp_str,
                            "message": log.strip(),
                            "title": title,
                            "category": category,
                            "job": job,
                            "query": query,
                            "start_offset": start_offset,
                            "end_offset": end_offset,
                            "mode": mode,
                            "polling_delay": polling_delay,
                            "include_bundle_header": cfg.get("include_bundle_header", False),
                            "mentions": cfg.get("mentions", []),
                            "from_previous_state": int(ts_val) < last_restart_ns
                        }
                        log_lines.append(log_entry)
                        new_entries.append({'id': log_id, 'ts': ts_int})

                if log_lines:
                    has_alert = True
                    max_ts = max([int(l["timestamp_ns"]) for l in log_lines])
                    all_entries_to_store = processed_entries + new_entries
                    pruned_entries = prune_processed_ids(all_entries_to_store, max_ts, processed_ids_window_ns)

                    updated_data[key] = {
                        "last_ts": max_ts,
                        "processed_entries": pruned_entries
                    }

                    if mode == "bundle" and polling_delay > 1:
                        alert_id = generate_alert_id(cfg)
                        state = load_polling_state(alert_id, config, eco_mode_active=eco_mode_active)

                        state["logs"].extend(log_lines)
                        state["count"] += 1

                        print(json.dumps({
                            "level": "DEBUG",
                            "type": "POLLING_STATE",
                            "file": f"{alert_id}.json",
                            "job": job,
                            "count": state["count"],
                            "logs_new": len(log_lines),
                            "logs_total": len(state['logs'])
                        }, ensure_ascii=False))

                        if state["count"] < polling_delay:
                            save_polling_state(alert_id, state, config, eco_mode_active=eco_mode_active)
                            continue

                        log_lines = state["logs"]

                        count_prev = len([l for l in log_lines if l.get("from_previous_state")])
                        count_curr = len(log_lines) - count_prev
                        print(json.dumps({
                            "level": "INFO",
                            "type": "POLLING_STATE_FLUSH_SPLIT",
                            "file": f"{alert_id}.json",
                            "count_prev": count_prev,
                            "count_curr": count_curr
                        }, ensure_ascii=False))

                        reset_polling_state(alert_id, config, eco_mode_active=eco_mode_active)

                    for log in log_lines:
                        alert_queue.put(log)

                if len(values) == limit:
                    print(f"[WARNING] Query '{title}' hasilnya mencapai LIMIT={limit}. Pertimbangkan interval lebih pendek.")

        if not has_alert:
            print(f"[INFO] Tidak ada log yang terdeteksi pada polling ini ({now_jakarta()} WIB).")

        cleanup_counter += 1
        if cleanup_counter >= 10:
            ttl_seconds = config.get("POLLING_STATE_TTL_SECONDS")
            cleanup_old_polling_states(config, cutoff_seconds=ttl_seconds, eco_mode_active=eco_mode_active)
            cleanup_counter = 0

        last_data.update(updated_data)
        save_last_timestamps(last_data, config)  
        time.sleep(poll_interval)




## = =[ Procedure ] = == = == = == = == = == = == = == = == = == = == = == = == = = .
def process_alerts(config):
    bundle_store = {}
    last_eco_status = None  # Track perubahan status eco mode

    alert_queue = config["alert_queue"]
    default_bundle_mode = config["DEFAULT_BUNDLE_MODE"]
    eco_config = config["ECO_CONFIG"]
    grafana_base_url = config["GRAFANA_BASE_URL"]
    grafana_datasource_iud = config["GRAFANA_DATASOURCE_UID"]
    discord_log_char_limit = config["DISCORD_LOG_CHAR_LIMIT"]
    discord_max_length = config["DISCORD_MAX_LENGTH"]



    while True:
        while not alert_queue.empty():
            log = alert_queue.get()
            mode = log.get("mode", default_bundle_mode)
            key = f"{log['title']}::{log['job']}"

            eco_active = is_eco_mode_active(datetime.now(), eco_config)
            include_single = eco_config.get("include_single_mode", False)

            print(json.dumps({
                "DEBUG": "ALERT_QUEUE_LOG_RECEIVED",
                "eco_mode_active": eco_active,
                "include_single_mode": include_single,
                "mode": mode,
                "key": key,
                "log_short": log.get("message", "")[:60]
            }, ensure_ascii=False))

            # === [ECO MODE AKTIF] Tambahkan semua alert (bundle maupun single) ke bundle_store ===
            if eco_active and include_single:
                if mode in ["bundle", "single"]:
                    print(json.dumps({
                        "DEBUG": "ECO MODE ALERT STORED TO BUNDLE_STORE",
                        "mode": mode,
                        "key": key,
                        "job": log["job"],
                        "title": log["title"]
                    }, ensure_ascii=False))
                    bundle_store.setdefault(key, []).append(log)
                    continue

            # === [Normal Mode] Tambahkan hanya alert mode "bundle" ke bundle_store ===
            if mode == "bundle":
                bundle_store.setdefault(key, []).append(log)
                continue

            # === [Single Mode] Proses alert satuan ===
            try:
                log_dt = datetime.strptime(log["timestamp_iso"], "%Y-%m-%d %H:%M:%S")
                log_dt = pytz.timezone("Asia/Jakarta").localize(log_dt)
                start_dt = log_dt - timedelta(seconds=log["start_offset"])
                end_dt = log_dt + timedelta(seconds=log["end_offset"])

                grafana_url = generate_grafana_explore_url(
                    grafana_base_url,
                    grafana_datasource_iud,
                    log['query'],
                    start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    end_dt.strftime("%Y-%m-%d %H:%M:%S")
                )

                mentions = " ".join(log.get("mentions", []))

                log_message = log.get("message", "")
                if len(log_message) > discord_log_char_limit:
                    log_message = log_message[:discord_log_char_limit].rstrip() + "\n..."

                message = (
                    f"Alert: {log['title']}\n"
                    f"Category: {log['category']}\n"
                    f"Job: {log['job']}\n"
                    f"```json\n{log_message}\n```\n"
                    f"[Lihat di Grafana Explore]({grafana_url})\n"
                    f"{mentions}"
                    + "\n\u200B\n"
                )

                if is_content_suspicious(config,message):
                    print(f"[WARNING] Payload SINGLE mencurigakan. Menampilkan isi:")
                    print(json.dumps({"content": message}, ensure_ascii=False, indent=2))
                elif len(message) > discord_max_length:
                    print(f"[WARNING] SINGLE message terlalu panjang ({len(message)} > {discord_max_length}), tidak dikirim.")
                else:
                    log_with_timestamp("▫️ SINGLE MODE - Proses: Ringkasan", context="single_mode_status")
                    send_discord_alert(config, message)

                print(json.dumps({
                    "level": "DEBUG",
                    "type": "SINGLE_ALERT_SENT",
                    "title": log['title'],
                    "job": log['job'],
                    "category": log['category']
                }, ensure_ascii=False))

            except Exception as e:
                print(f"[ERROR] Gagal proses SINGLE alert: {e}")


        # === BUNDLE MODE ===
        if bundle_store:
            try:
                eco_status = is_eco_mode_active(datetime.now(), eco_config)

                # Cetak transisi mode sekali
                if last_eco_status != eco_status:
                    print(f"[DEBUG] ECO MODE berubah: {'AKTIF' if eco_status else 'NON-AKTIF'}")
                    last_eco_status = eco_status

                if eco_status:
                    log_with_timestamp("🔹 ECO MODE AKTIF - Proses: Ringkasan bundle eco", context="bundle_eco_mode_status")


                    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                    # print(f"[DEBUG] 🔥 Simpan sample bundle_store (for tester.py) → sample_bundle_store.json")
                    # with open("sample_bundle_store.json", "w", encoding="utf-8") as f:
                    #     json.dump(bundle_store, f, ensure_ascii=False, indent=2)       
                    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

                    send_discord_bundle_messages_eco(config,bundle_store)
                else:
                    log_with_timestamp("🔸 ECO MODE NON-AKTIF - Proses: Bundle mode normal", context="bundle_normal_mode_status")
                    send_discord_bundle_messages(config,bundle_store)

            except Exception as e:
                print(f"[ERROR] Gagal kirim BUNDLE alert: {e}")

        # Bersihkan bundle dan tunggu untuk siklus berikutnya
        bundle_store.clear()
        eco_sleep = config.get("ECO_POLL_INTERVAL") if last_eco_status else 1
        time.sleep(eco_sleep)
