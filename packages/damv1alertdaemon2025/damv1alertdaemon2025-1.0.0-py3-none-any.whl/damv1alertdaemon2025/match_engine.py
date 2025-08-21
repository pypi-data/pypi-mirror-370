# match_engine.py
# Dummy placeholder – untuk pengembangan filtering lebih kompleks
def should_alert(log_line: str) -> bool:
    """
    Tentukan apakah sebuah log line layak dijadikan alert.
    Saat ini default selalu True, tapi bisa dimodifikasi
    untuk filtering lebih kompleks.
    
    Args:
        log_line (str): Satu baris log dari Loki.

    Returns:
        bool: True jika log layak dijadikan alert.
    """
    # Contoh sederhana: semua log di-allow
    return True

    # Contoh filter IP:
    # return "192.168." in log_line

    # Contoh filter keyword tertentu:
    # return "ERROR" in log_line or "FATAL" in log_line