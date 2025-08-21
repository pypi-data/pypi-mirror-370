# ===========================================================
# Module   : steps.py
# Purpose  : Alert Daemon 2025 - Startup & Thread Management
# ===========================================================

import os
import time
import pytz
import json
import threading
import traceback
import subprocess
from datetime import datetime
from .polling import check_loki_ready, is_eco_mode_active, enqueue_alerts, process_alerts
from .discord_cleanup_daemon import start_cleanup_thread


class Alert:
    _step_completed = set()
    _active_threads = {}

    # ===========================================================
    # Banner ASCII
    # ===========================================================
    @staticmethod
    def print_banner():
        try:
            from pyfiglet import Figlet
            f = Figlet(font="slant")
            print(f.renderText("Alert Daemon 2025"), flush=True)
            return
        except ImportError:
            pass

        for cmd in [["figlet", "-f", "slant", "Alert Daemon 2025"],
                    ["toilet", "-f", "slant", "Alert Daemon 2025"]]:
            try:
                output = subprocess.check_output(cmd, text=True)
                print(output, flush=True)
                return
            except Exception:
                continue

        print("=== ALERT DAEMON 2025 ===", flush=True)

    # ===========================================================
    # Thread Management
    # ===========================================================
    @classmethod
    def start_daemon_thread(cls, name, target, args=()):
        def wrapper():
            print(f"[DEBUG] Thread '{name}' dimulai...", flush=True)
            try:
                target(*args)
            except Exception as e:
                print(f"[ERROR] Thread '{name}' gagal: {e}", flush=True)
                traceback.print_exc()

        t = threading.Thread(target=wrapper, daemon=True, name=name)
        t.start()
        cls._active_threads[name] = t
        print(f"    →   Thread '{name}' status: {'alive' if t.is_alive() else 'dead'}", flush=True)
        return t

    @classmethod
    def monitor_threads(cls, interval=30):
        thread_names = list(cls._active_threads.keys())
        print(f"[DEBUG] Thread monitor dimulai, memantau: {', '.join(thread_names)}", flush=True)

        while True:
            all_alive = True
            for name, thread in cls._active_threads.items():
                if not thread.is_alive():
                    all_alive = False
                    print(f"[ERROR] Thread '{name}' tidak berjalan! Perlu restart.", flush=True)

            if all_alive:
                print("[DEBUG] Thread monitor status: alive - semua thread berjalan normal", flush=True)

            time.sleep(interval)

    # ===========================================================
    # Startup Steps
    # ===========================================================
    @classmethod
    def step1_validate_loki(cls, config):
        loki_url = config.get("LOKI_URL")
        if not loki_url or loki_url.lower() == "none":
            raise RuntimeError("LOKI_URL tidak ditemukan")
        if not check_loki_ready(loki_url):
            raise RuntimeError(f"Loki tidak siap di {loki_url}")
        cls._step_completed.add(1)

    @classmethod
    def step2_info_eco_mode(cls, config):
        eco_config = config.get("ECO_CONFIG", {})
        tz = eco_config.get("timezone", "Asia/Jakarta")
        now_str = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S")

        if is_eco_mode_active(datetime.now(), eco_config):
            print(f"[DEBUG] ECO MODE AKTIF - Time now: {now_str} ({tz})", flush=True)
            print(json.dumps({
                "DEBUG": "ECO MODE CONFIG",
                "eco_mode": eco_config
            }, indent=2), flush=True)
        else:
            print(f"[DEBUG] ECO MODE NON-AKTIF - Time now: {now_str} ({tz})", flush=True)

        cls._step_completed.add(2)

    @classmethod
    def step3_start_main_threads(cls, config):
        if 1 not in cls._step_completed:
            raise RuntimeError("Step1 (validate loki) harus dijalankan dulu")

        restart_info = {"last_restart_time_ns": int(time.time() * 1e9)}
        os.makedirs(os.path.dirname(config["RESTART_INFO_PATH"]), exist_ok=True)
        with open(config["RESTART_INFO_PATH"], "w") as f:
            json.dump(restart_info, f)

        print(f"[INFO] Restart time dicatat: {restart_info['last_restart_time_ns']}", flush=True)
        print("[INFO] Memulai alert daemon polling ke Loki...", flush=True)

        cls.start_daemon_thread("enqueue_alerts", enqueue_alerts, (config,))
        cls.start_daemon_thread("process_alerts", process_alerts, (config,))
        cls.start_daemon_thread("start_cleanup_thread", start_cleanup_thread, (config,))
        cls.start_daemon_thread("thread_monitor", cls.monitor_threads, (config.get("THREAD_MONITOR_INTERVAL", 30),))

        cls._step_completed.add(3)
