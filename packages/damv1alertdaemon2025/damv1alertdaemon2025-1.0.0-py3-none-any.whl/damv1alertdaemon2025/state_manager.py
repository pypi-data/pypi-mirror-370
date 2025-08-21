# polling_state_manager.py
import os
import json
import hashlib
import time

## -- [ Initialize ] ---------------------------------------------------------------
DEFAULT_POLLING_STATE_DIR = "temp/polling_state"
DEFAULT_POLLING_STATE_ECO_DIR = "temp/polling_state_eco"

def get_default_config():
    return {
        "DEFAULT_POLLING_STATE_DIR": DEFAULT_POLLING_STATE_DIR,
        "DEFAULT_POLLING_STATE_ECO_DIR": DEFAULT_POLLING_STATE_ECO_DIR   
    }

## -- [ 001 ] ----------------------------------------------------------------------
def get_polling_state_dir(config, eco_mode_active=False):
    """Ambil direktori polling state dari config, fallback ke default"""
    return config.get(
        "POLLING_STATE_ECO_DIR" if eco_mode_active else "POLLING_STATE_DIR",
        config.get("DEFAULT_POLLING_STATE_ECO_DIR") if eco_mode_active else config.get("DEFAULT_POLLING_STATE_DIR")
    )

## -- [ 002 ] ----------------------------------------------------------------------
def generate_alert_id(cfg):
    """Generate hash unik untuk alert berdasarkan title, query, dan job"""
    base = f"{cfg['title']}::{cfg['query']}::{cfg.get('job', '')}"
    return hashlib.md5(base.encode()).hexdigest()

## -- [ 003 ] ----------------------------------------------------------------------
def get_polling_state_path(alert_id, directory):
    """Buat path file polling state"""
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"{alert_id}.json")

## -- [ 004 ] ----------------------------------------------------------------------
def load_polling_state(alert_id, config, eco_mode_active=False):
    """Load polling state dari file"""
    directory = get_polling_state_dir(config, eco_mode_active)
    path = get_polling_state_path(alert_id, directory)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Gagal membaca polling state {path}: {e}")
    return {"logs": [], "count": 0}

## -- [ 005 ] ----------------------------------------------------------------------
def save_polling_state(alert_id, state, config, eco_mode_active=False):
    """Simpan polling state ke file"""
    directory = get_polling_state_dir(config, eco_mode_active)
    path = get_polling_state_path(alert_id, directory)
    try:
        with open(path, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"[WARNING] Gagal menyimpan polling state {path}: {e}")

## -- [ 006 ] ----------------------------------------------------------------------
def reset_polling_state(alert_id, config, eco_mode_active=False):
    """Reset polling state ke kosong"""
    save_polling_state(alert_id, {"logs": [], "count": 0}, config, eco_mode_active)

## -- [ 007 ] ----------------------------------------------------------------------
def delete_polling_state(alert_id, config, eco_mode_active=False):
    """Hapus file polling state"""
    directory = get_polling_state_dir(config, eco_mode_active)
    path = get_polling_state_path(alert_id, directory)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"[WARNING] Gagal menghapus polling state {path}: {e}")

## -- [ 008 ] ----------------------------------------------------------------------
def cleanup_old_polling_states(config, cutoff_seconds=3600, eco_mode_active=False):
    """Hapus polling state yang sudah lama"""
    polling_dir = get_polling_state_dir(config, eco_mode_active)
    if not os.path.exists(polling_dir):
        return

    now = time.time()
    for file in os.listdir(polling_dir):
        filepath = os.path.join(polling_dir, file)
        try:
            if os.path.isfile(filepath):
                mtime = os.path.getmtime(filepath)
                if now - mtime > cutoff_seconds:
                    os.remove(filepath)
                    print(f"[DEBUG] [POLLING CLEANUP] Hapus file: {filepath}")
        except Exception as e:
            print(f"[ERROR] Gagal menghapus polling state {filepath}: {e}")

## -- [ 009 ] ----------------------------------------------------------------------
def read_polling_state(alert_key, config, eco_mode_active=False):
    """Baca polling state manual"""
    directory = get_polling_state_dir(config, eco_mode_active)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{alert_key}.json")
    try:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARNING] Gagal membaca polling state: {e}")
    return {"logs": [], "file_name": f"{alert_key}.json"}

## -- [ 010 ] ----------------------------------------------------------------------
def write_polling_state(alert_key, data, config, eco_mode_active=False):
    """Tulis polling state manual"""
    directory = get_polling_state_dir(config, eco_mode_active)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{alert_key}.json")
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"[WARNING] Gagal menulis polling state: {e}")