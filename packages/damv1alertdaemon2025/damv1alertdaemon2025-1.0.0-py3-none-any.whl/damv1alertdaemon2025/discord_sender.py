import os
import json
import re
import requests
from datetime import datetime, timedelta
from urllib.parse import unquote
from .grafana_url_generator import generate_grafana_explore_url
import time
import pytz

DEFAULT_OFFSET_ECO = 3
DISCORD_MAX_LENGTH = 2000
DISCORD_LOG_CHAR_LIMIT = 800
RESTART_INFO_PATH = "./temp/last_restart_info.json"
KNOWN_SAFE_PATTERNS_PATH = "./temp/known_safe_patterns.json"
KNOWN_SAFE_PATTERNS_META_PATH = "./temp/known_safe_patterns_meta.json"


## -- [ Initialize ] ---------------------------------------------------------------
def get_default_config():
    return {
        "DEFAULT_OFFSET_ECO": DEFAULT_OFFSET_ECO,
        "DISCORD_MAX_LENGTH": DISCORD_MAX_LENGTH,
        "DISCORD_LOG_CHAR_LIMIT": DISCORD_LOG_CHAR_LIMIT,
        "RESTART_INFO_PATH": RESTART_INFO_PATH,
        "KNOWN_SAFE_PATTERNS_PATH": KNOWN_SAFE_PATTERNS_PATH,
        "KNOWN_SAFE_PATTERNS_META_PATH": KNOWN_SAFE_PATTERNS_META_PATH,

        "DISCORD_WEBHOOK_URL": None,
        "GRAFANA_BASE_URL": None,
        "GRAFANA_DATASOURCE_UID": None,
        "DEFAULT_START_OFFSET": None,
        "DEFAULT_END_OFFSET": None,
        "KNOWN_SAFE_PATTERNS_ROTATE_HOURS": None      
    }



## -- [ 001 ] ----------------------------------------------------------------------
def send_discord_alert(config, message):
    webhook_url = config.get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("[ERROR] DISCORD_WEBHOOK_URL tidak dikonfigurasi. Pesan tidak dikirim.")
        return

    try:
        response = requests.post(webhook_url, json={"content": message})
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Gagal mengirim alert ke Discord: {e}")


## -- [ 002 ] ----------------------------------------------------------------------
def should_rotate_known_patterns(config):
    meta_path = config.get("KNOWN_SAFE_PATTERNS_META_PATH")
    rotate_hours = config.get("KNOWN_SAFE_PATTERNS_ROTATE_HOURS", 24)

    try:
        with open(meta_path) as f:
            meta = json.load(f)
            last_ts = meta.get("last_updated_ts", 0)
    except Exception:
        last_ts = 0

    now_ts = int(time.time())
    elapsed_hours = (now_ts - last_ts) / 3600
    return elapsed_hours >= rotate_hours


## -- [ 003 ] ----------------------------------------------------------------------
def rotate_known_patterns_if_needed(config):
    if should_rotate_known_patterns(config):
        rotate_hours = config.get("KNOWN_SAFE_PATTERNS_ROTATE_HOURS", 24)
        print(f"[INFO] Rotating known_safe_patterns.json after {rotate_hours}h.")

        patterns_path = config.get("KNOWN_SAFE_PATTERNS_PATH")
        meta_path = config.get("KNOWN_SAFE_PATTERNS_META_PATH")

        try:
            if os.path.exists(patterns_path):
                os.remove(patterns_path)
        except Exception as e:
            print(f"[ERROR] Gagal hapus {patterns_path}: {e}")

        try:
            with open(meta_path, "w") as f:
                json.dump({"last_updated_ts": int(time.time())}, f)
        except Exception as e:
            print(f"[ERROR] Gagal update meta rotasi: {e}")


## -- [ 004 ] ----------------------------------------------------------------------
def load_known_safe_patterns(config):
    know_safe_patterns_path = config.get("KNOWN_SAFE_PATTERNS_PATH")

    try:
        with open(know_safe_patterns_path) as f:
            return json.load(f)
    except Exception:
        return []

## -- [ 005 ] ----------------------------------------------------------------------
def save_known_safe_patterns(config, patterns):
    know_safe_patterns_path = config.get("KNOWN_SAFE_PATTERNS_PATH")
    os.makedirs(os.path.dirname(know_safe_patterns_path), exist_ok=True)
    with open(know_safe_patterns_path, "w") as f:
        json.dump(patterns, f, indent=2)

## -- [ 006 ] ----------------------------------------------------------------------
def generate_safe_pattern_regex(part: str) -> str:
    escaped = re.escape(part)

    # Pengecualian: Grafana Explore link
    escaped = re.sub(
        r"(\\\[Lihat\\ di\\ Grafana\\ Explore\\\]\(https://grafana[^)]+\\\))",
        r"[Lihat di Grafana Explore](https://grafana.*)",
        escaped
    )

    substitutions = [
        (r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} WIB", r".* WIB"),
        (r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} WIB", r".* WIB"),
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?", r".*"),
        (r"\d+\.\d+", r"\\d+\\.\\d+"),
        (r"\d+", r"\\d+"),
        (r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", r".*"),
        (r"https:\\/\\/[^\\s]+", r"https://.*"),
    ]

    for pattern, replacement in substitutions:
        escaped = re.sub(pattern, replacement, escaped)

    return f"(?s){escaped}"

## -- [ 007 ] ----------------------------------------------------------------------
def is_content_suspicious(config, s: str) -> bool:
    known_patterns = load_known_safe_patterns(config)
    for pattern in known_patterns:
        try:
            if re.fullmatch(pattern, s, re.DOTALL):
                return False
        except re.error:
            continue

    if "\uFFFD" in s:
        return True
    if any(ord(c) < 32 and c not in ['\n', '\t'] for c in s):
        return True
    if any(0xD800 <= ord(c) <= 0xDFFF for c in s):
        return True
    try:
        json.dumps({"content": s}, ensure_ascii=False)
    except Exception:
        return True
    return False

## -- [ 008 ] ----------------------------------------------------------------------
def get_restart_time_label(config):
    restart_info_path = config["RESTART_INFO_PATH"]
    try:
        with open(restart_info_path) as f:
            restart_info = json.load(f)
            ns = int(restart_info.get("last_restart_time_ns", 0))
            dt = datetime.fromtimestamp(ns / 1e9, tz=pytz.timezone("Asia/Jakarta"))
            return dt.strftime("Restart Daemon: %Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return "Restart Daemon: (tidak diketahui)"


## -- [ 009 ] ----------------------------------------------------------------------
def get_loki_log_count(config, query, start_iso, end_iso):
    loki_url = f"{config.get('LOKI_URL')}/loki/api/v1/query_range"
    params = {
        "query": query,
        "start": int(datetime.fromisoformat(start_iso).timestamp() * 1e9),
        "end": int(datetime.fromisoformat(end_iso).timestamp() * 1e9),
        "limit": 5000,
        "direction": "FORWARD"
    }

    response = requests.get(loki_url, params=params)
    response.raise_for_status()
    data = response.json()

    count = 0
    if data["status"] == "success" and "result" in data["data"]:
        for stream in data["data"]["result"]:
            count += len(stream.get("values", []))
    return count












## = =[ Procedure ] = == = == = == = == = == = == = == = == = == = == = == = == = = .
def build_section(config, logs_subset, label=None, tz=pytz.timezone("Asia/Jakarta"), log_char_limit=None, max_logs=2):
    log_char_limit = log_char_limit or config["DISCORD_LOG_CHAR_LIMIT"]

    sorted_subset = sorted(logs_subset, key=lambda x: int(x["timestamp_ns"]))
    polling_delay = sorted_subset[0].get("polling_delay", 1)
    polling_info = f" | Delay Polling: {polling_delay}x" if polling_delay > 1 else ""

    section_start_ns = int(sorted_subset[0]['timestamp_ns'])
    section_end_ns = int(sorted_subset[-1]['timestamp_ns'])
    section_start_dt = datetime.fromtimestamp(section_start_ns / 1e9, tz)
    section_end_dt = datetime.fromtimestamp(section_end_ns / 1e9, tz)

    start_label = section_start_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " WIB"
    end_label = section_end_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " WIB"
    range_label = f" | Time Range: {start_label} → {end_label}"

    meta = f"{label}\n" if label else ""
    meta += f"Buffered: {len(sorted_subset)} log(s){polling_info}{range_label}"

    displayed_logs = sorted_subset[:max_logs]
    combined = "\n".join(log["message"] for log in displayed_logs)
    if len(sorted_subset) > max_logs:
        combined += "\n..."
    if len(combined) > log_char_limit:
        combined = combined[:log_char_limit - 5] + "\n..."

    logs_block = f"```json\n{combined}\n```\n"

    start_offset = sorted_subset[0].get("start_offset", 0)
    end_offset = sorted_subset[0].get("end_offset", 0)
    start_range = section_start_dt - timedelta(seconds=start_offset)
    end_range = section_end_dt + timedelta(seconds=end_offset)

    query = sorted_subset[0]['query']
    grafana_url = generate_grafana_explore_url(
        config.get("GRAFANA_BASE_URL"),
        config.get("GRAFANA_DATASOURCE_UID"),
        query,
        start_range.strftime("%Y-%m-%d %H:%M:%S"),
        end_range.strftime("%Y-%m-%d %H:%M:%S")
    )

    try:
        loki_log_count = get_loki_log_count(config, query, start_range.isoformat(), end_range.isoformat())
        log_count_label = f" | Grafana Context: {loki_log_count} log(s)"
    except Exception as e:
        print(f"[WARNING] Gagal mengambil count logs dari Loki: {e}")
        log_count_label = ""

    raw_log_label = ""
    try:
        raw_log_count = get_loki_log_count(config, query, section_start_dt.isoformat(), section_end_dt.isoformat())
        if section_start_dt != section_end_dt or raw_log_count != 0:
            raw_log_label = f" | Range-Exact: {raw_log_count} log(s)"
    except Exception as e:
        print(f"[WARNING] Gagal ambil raw log count dari Loki: {e}")

    meta += raw_log_label
    grafana_link = f"[Lihat di Grafana Explore]({grafana_url}){log_count_label}\n"
    mentions = " ".join(sorted_subset[0].get("mentions", [])) + "\n" if sorted_subset[0].get("mentions") else ""

    section = meta + logs_block + grafana_link + mentions + "\n\u200B\n"
    return section, {
        "meta_len": len(meta),
        "logs_len": len(combined),
        "link_len": len(grafana_link + mentions),
        "grafana_url": grafana_url
    }


## = =[ Procedure ] = == = == = == = == = == = == = == = == = == = == = == = == = = .
def send_discord_bundle_messages(config, bundle_store):
    rotate_known_patterns_if_needed(config)
    tz = pytz.timezone("Asia/Jakarta")
    parts = []
    part_index = 1
    serial_index = 1
    max_length = config.get("DISCORD_MAX_LENGTH")

    bundle_items = [
        (key, logs) for key, logs in bundle_store.items()
        if logs and logs[0].get("mode", "bundle") == "bundle"
    ]
    if not bundle_items:
        return

    all_logs = [log for _, logs in bundle_items for log in logs]
    header = "[ 📦 Bundles ]\n"

    show_header = any(log.get("include_bundle_header", False) for _, logs in bundle_items for log in logs)
    if show_header and all_logs:
        sorted_all = sorted(all_logs, key=lambda x: int(x['timestamp_ns']))
        start_all = datetime.fromtimestamp(int(sorted_all[0]['timestamp_ns']) / 1e9, tz)
        end_all = datetime.fromtimestamp(int(sorted_all[-1]['timestamp_ns']) / 1e9, tz)
        header += (
            f"Waktu Buffer:\n- Start: {start_all.strftime('%Y-%m-%d %H:%M:%S')} WIB → "
            f"End: {end_all.strftime('%Y-%m-%d %H:%M:%S')} WIB\n"
        )

        has_prev = any(log.get("from_previous_state", False) for log in all_logs)
        has_curr = any(not log.get("from_previous_state", True) for log in all_logs)
        if has_prev and has_curr:
            header += (
                "Note:\nLog ini sebagian merupakan hasil polling dari sebelum project restart.\n"
                "[PREVIOUS STATE] → sisa sebelum restart\n"
                "[CURRENT POLLING] → setelah restart\n"
            )
        header += "\n"

    for key, logs in bundle_items:
        sorted_logs = sorted(logs, key=lambda x: int(x['timestamp_ns']))
        prev_logs = [l for l in sorted_logs if l.get("from_previous_state")]
        curr_logs = [l for l in sorted_logs if not l.get("from_previous_state")]

        if prev_logs and not curr_logs:
            continue

        section_bundles = []
        restart_label = get_restart_time_label(config)

        if prev_logs:
            sec, _ = build_section(config, prev_logs, f"[PREVIOUS STATE] {restart_label}")
            section_bundles.append(("1", sec))

        if curr_logs:
            label = f"[CURRENT POLLING] {restart_label}" if prev_logs else None
            sec, _ = build_section(config, curr_logs, label)
            suffix = "2" if prev_logs else None
            section_bundles.append((suffix, sec))

        multiple_parts = len(section_bundles) > 1
        total_items = len(bundle_items)

        for suffix, sec_content in section_bundles:
            prefix = f"{serial_index}.{suffix} |  " if multiple_parts and suffix else \
                     f"{serial_index}. |  " if total_items > 1 else ""

            message_header = (
                f"{prefix}Alert: {sorted_logs[0]['title']}\n"
                f"Category: {sorted_logs[0]['category']}\n"
                f"Job: {sorted_logs[0]['job']}\n"
            )
            full_message = (header if part_index == 1 else "") + message_header + sec_content

            if len(full_message) > max_length:
                print(f"[WARNING] Part-{part_index} melebihi batas karakter Discord. Tidak dikirim.")
                continue

            parts.append(full_message)
            part_index += 1
        serial_index += 1

    for idx, part in enumerate(parts):
        suspicious = is_content_suspicious(config, part)
        print(f"[DEBUG] Payload part-{idx+1} valid. Panjang: {len(part)}")

        if suspicious:
            print(f"[WARNING] Payload part-{idx+1} mencurigakan. Menampilkan isi:")
            print(json.dumps({"content": part}, ensure_ascii=False, indent=2))

        if len(part) > max_length:
            continue

        try:
            response = requests.post(config.get("DISCORD_WEBHOOK_URL"), json={"content": part})
            response.raise_for_status()
            if suspicious:
                pattern = generate_safe_pattern_regex(part)
                patterns = load_known_safe_patterns(config)
                if not any(re.fullmatch(p, part, re.DOTALL) for p in patterns):
                    patterns.append(pattern)
                    save_known_safe_patterns(config, patterns)
                    print(f"[INFO] Pola aman baru ditambahkan.")
        except Exception as e:
            print(f"[ERROR] Gagal mengirim bundle alert part-{idx+1} ke Discord: {e}")



## = =[ Procedure ] = == = == = == = == = == = == = == = == = == = == = == = == = = .
def send_discord_bundle_messages_eco(config, bundle_store):
    print(json.dumps({
        "DEBUG": "[ECO] Mulai kirim bundle store",
        "total_keys": len(bundle_store),
        "keys": list(bundle_store.keys())
    }, ensure_ascii=False))

    rotate_known_patterns_if_needed(config)
    tz = pytz.timezone("Asia/Jakarta")
    parts = []
    max_length = config.get("DISCORD_MAX_LENGTH")
    part_content = ""

    for key, logs in bundle_store.items():
        print(json.dumps({
            "DEBUG": "[ECO] Periksa key",
            "key": key,
            "jumlah_log": len(logs),
            "mode": logs[0].get("mode") if logs else "N/A",
            "log_titles": [log.get("title") for log in logs]
        }, ensure_ascii=False))

    all_logs = [log for _, logs in bundle_store.items() for log in logs if logs]
    if not all_logs:
        print("[INFO] [ECO] Tidak ada log yang dapat dikirim.")
        return

    sorted_all = sorted(all_logs, key=lambda x: int(x.get('timestamp_ns', 0)))
    start_dt = datetime.fromtimestamp(int(sorted_all[0].get('timestamp_ns', 0)) / 1e9, tz)
    end_dt = datetime.fromtimestamp(int(sorted_all[-1].get('timestamp_ns', 0)) / 1e9, tz)

    eco_header_main = (
        f"[ 📦 Bundles Eco-mode - polling_state_eco ] Time Range: "
        f"{start_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} WIB → "
        f"{end_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} WIB\n"
    )

    part_content = eco_header_main
    serial_index = 1
    total_items = len(bundle_store)

    for key, logs in bundle_store.items():
        if not logs:
            print(f"[SKIP] [ECO] Key '{key}' kosong. Skip.")
            continue

        first_log = logs[0]
        query = first_log.get('query', '')
        logs_sorted = sorted(logs, key=lambda x: x.get('timestamp_ns', 0))
        raw_start_ns = int(logs_sorted[0].get('timestamp_ns', 0))
        raw_end_ns = int(logs_sorted[-1].get('timestamp_ns', 0))

        offset = config.get('DEFAULT_OFFSET_ECO')
        section_start = datetime.fromtimestamp((raw_start_ns / 1e9) - offset, tz)
        section_end = datetime.fromtimestamp((raw_end_ns / 1e9) + offset, tz)

        try:
            loki_count = get_loki_log_count(config, query, section_start.isoformat(), section_end.isoformat())
        except Exception:
            loki_count = "?"

        grafana_url = generate_grafana_explore_url(
            config.get("GRAFANA_BASE_URL"),
            config.get("GRAFANA_DATASOURCE_UID"),
            query,
            section_start.strftime("%Y-%m-%d %H:%M:%S"),
            section_end.strftime("%Y-%m-%d %H:%M:%S")
        )

        line = (
            f"{serial_index}. | Alert: {first_log.get('title', '?')} | Category: {first_log.get('category', '?')} | "
            f"Job: {first_log.get('job', '?')} | [Lihat di Grafana Explore]({grafana_url}) | Grafana Context: {loki_count} log(s)\n"
        ) if total_items > 1 else (
            f"Alert: {first_log.get('title', '?')} | Category: {first_log.get('category', '?')} | "
            f"Job: {first_log.get('job', '?')} | [Lihat di Grafana Explore]({grafana_url}) | Grafana Context: {loki_count} log(s)\n"
        )

        if len(part_content) + len(line) > max_length - 100:
            parts.append(part_content)
            part_content = line
        else:
            part_content += line

        serial_index += 1

    if part_content.strip():
        part_content += "\u200B\n"
        parts.append(part_content)

    for idx, part in enumerate(parts):
        suspicious = is_content_suspicious(config, part)
        print(json.dumps({
            "DEBUG": f"[ECO] Payload part-{idx+1} valid",
            "panjang": len(part),
            "curiga": suspicious
        }, ensure_ascii=False))
        
        if suspicious:
            print(f"[WARNING] [ECO] Payload part-{idx+1} mencurigakan.")
            print(json.dumps({"content": part}, ensure_ascii=False, indent=2))
        elif len(part) > max_length:
            print(f"[WARNING] [ECO] Part-{idx+1} melebihi batas karakter Discord. Dibatasi.")
            continue

        try:
            response = requests.post(config.get("DISCORD_WEBHOOK_URL"), json={"content": part})
            response.raise_for_status()
            print(f"[INFO] [ECO] Part-{idx+1} berhasil dikirim ke Discord.")

            if suspicious:
                pattern = generate_safe_pattern_regex(part)
                patterns = load_known_safe_patterns(config)
                if not any(re.fullmatch(p, part, re.DOTALL) for p in patterns):
                    patterns.append(pattern)
                    save_known_safe_patterns(config, patterns)
                    print(f"[INFO] [ECO] Pola aman baru ditambahkan.")

        except Exception as e:
            print(f"[ERROR] Gagal mengirim ECO BUNDLE part-{idx+1} ke Discord: {e}")