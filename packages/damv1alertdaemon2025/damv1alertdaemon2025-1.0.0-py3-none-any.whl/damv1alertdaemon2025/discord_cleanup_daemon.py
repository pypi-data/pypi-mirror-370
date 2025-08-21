# discord_cleanup_daemon.py

import os
import re
import json
import asyncio
import pytz
import threading
from datetime import datetime, timezone
import discord


# =========================
# Helper
# =========================
def parse_time_to_seconds(value):
    """Konversi '20m', '45s', '2h', '1d' jadi detik."""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip().lower()
        m = re.match(r"^(\d+(\.\d+)?)([smhd])?$", s)
        if m:
            num = float(m.group(1))
            unit = (m.group(3) or "s").lower()
            if unit == "s":
                return num
            elif unit == "m":
                return num * 60
            elif unit == "h":
                return num * 3600
            elif unit == "d":
                return num * 86400
        return float(s)
    except Exception:
        return None


def to_bool_loose(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "1", "yes", "y"):
            return True
        if s in ("false", "0", "no", "n"):
            return False
    return None


# =========================
# Load patterns dari ALERT_CONFIG_PATH
# =========================
def load_config(config):
    patterns_content = []
    patterns_embed = []
    delete_conditions = {}
    alert_config_path = config.get("ALERT_CONFIG_PATH", "./alert-config/alerts.json")
    try:
        with open(alert_config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"[ERROR] Gagal load ALERT_CONFIG_PATH '{alert_config_path}': {e}")
        return patterns_content, patterns_embed, delete_conditions

    patterns_section = cfg.get("patterns_messages_discord", {}) or {}
    patterns_content = patterns_section.get("KNOWN_PATTERNS_CONTENT", []) or []
    patterns_embed = patterns_section.get("KNOWN_PATTERNS_EMBED", []) or []

    delete_conditions = cfg.get("delete_conditions") or cfg.get("discord_delete_filters") or {}

    # Cetak konfigurasi awal
    if delete_conditions:
        author = delete_conditions.get("author", "unknown")
        channel = delete_conditions.get("channel_name", "").lstrip("#")
        guild = delete_conditions.get("guild_name", "unknown")
        status = delete_conditions.get("status_content", "unknown")
        age = delete_conditions.get("created_at_older_than", "unknown")
        age_human = _humanize_duration(age) if age != "unknown" else "unknown"

        print(f"CONFIGURED - DISCORD CLEANUP MODE: Bot: {author} → channel: #{channel} → "
              f"server (guild): {guild} → status: {status} → "
              f"Hanya hapus pesan lebih lama dari: {age_human}")
    else:
        print("CONFIGURED - DISCORD CLEANUP MODE: Tidak ada filter penghapusan pesan.")

    return patterns_content, patterns_embed, delete_conditions


# Fungsi helper lokal (untuk load_config)
def _humanize_duration(duration: str) -> str:
    units = {"s": "detik", "m": "menit", "h": "jam", "d": "hari"}
    if not duration or duration == "unknown":
        return "unknown"
    num = ''.join(filter(str.isdigit, duration))
    unit = duration[-1].lower() if duration else "s"
    return f"{num} {units.get(unit, unit)}"


# =========================
# Pattern detection
# =========================
def detect_pattern(text, known_patterns, source_name):
    if not text:
        return {"status": "unrecognized", "pattern_source": "UNKNOWN", "format_name": None}
    for pat in known_patterns:
        regex = pat.get("regex")
        if not regex:
            continue
        try:
            if re.match(regex, text, re.MULTILINE):
                return {"status": "recognized", "pattern_source": source_name,
                        "format_name": pat.get("name"), "matched_regex": regex}
        except re.error as e:
            return {"status": "regex_error", "pattern_source": source_name,
                    "format_name": pat.get("name"), "error": str(e), "matched_regex": regex}
    return {"status": "unrecognized", "pattern_source": "UNKNOWN", "format_name": None}


# =========================
# Delete condition checker
# =========================
def check_delete_conditions_with_trace(msg, status_info, delete_conditions):
    cond = delete_conditions or {}
    trace = []
    passed = True

    # author
    expected_author = cond.get("author")
    actual_author = str(msg.author) if msg.author else None
    ok_author = (expected_author is None) or (expected_author == actual_author)
    trace.append(("author", ok_author, f"expected={expected_author} actual={actual_author}"))
    if not ok_author:
        passed = False

    # is_bot
    if "is_bot" in cond:
        expected_is_bot = to_bool_loose(cond.get("is_bot"))
        actual_is_bot = bool(msg.author.bot) if msg.author else False
        ok_bot = (expected_is_bot is None) or (expected_is_bot == actual_is_bot)
        trace.append(("is_bot", ok_bot, f"expected={expected_is_bot} actual={actual_is_bot}"))
        if not ok_bot:
            passed = False

    # channel_name
    expected_channel = cond.get("channel_name")
    actual_channel = f"#{msg.channel.name}" if getattr(msg, "channel", None) and getattr(msg.channel, "name", None) else None
    alt_expected = expected_channel[1:] if isinstance(expected_channel, str) and expected_channel.startswith("#") else None
    ok_channel = (expected_channel is None) or (actual_channel == expected_channel) or (
                alt_expected == (msg.channel.name if msg.channel else None))
    trace.append(("channel_name", ok_channel, f"expected={expected_channel} actual={actual_channel}"))
    if not ok_channel:
        passed = False

    # guild_name
    expected_guild = cond.get("guild_name")
    actual_guild = msg.guild.name if getattr(msg, "guild", None) and getattr(msg.guild, "name", None) else None
    ok_guild = (expected_guild is None) or (expected_guild == actual_guild)
    trace.append(("guild_name", ok_guild, f"expected={expected_guild} actual={actual_guild}"))
    if not ok_guild:
        passed = False

    # status_content
    expected_status = cond.get("status_content")
    actual_status = status_info.get("status")
    ok_status = True
    if expected_status:
        if isinstance(expected_status, list):
            ok_status = any(str(e).strip().lower() == str(actual_status).strip().lower() or
                            str(e).strip().lower() in str(actual_status).strip().lower() for e in expected_status)
        else:
            es = str(expected_status).strip().lower()
            asv = str(actual_status).strip().lower()
            ok_status = (es == asv) or (es in asv) or (asv in es)
    trace.append(("status_content", ok_status, f"expected={expected_status} actual={actual_status}"))
    if not ok_status:
        passed = False

    # pattern_source
    expected_ps = cond.get("pattern_source")
    actual_ps = status_info.get("pattern_source")
    ok_ps = (expected_ps is None) or (expected_ps == actual_ps)
    trace.append(("pattern_source", ok_ps, f"expected={expected_ps} actual={actual_ps}"))
    if not ok_ps:
        passed = False

    # created_at threshold
    seconds_threshold = None
    if "created_at_hours_ago_gt" in cond:
        try:
            seconds_threshold = float(cond["created_at_hours_ago_gt"]) * 3600
        except Exception:
            pass
    if "created_at_older_than" in cond:
        parsed_seconds = parse_time_to_seconds(cond["created_at_older_than"])
        if parsed_seconds is not None:
            seconds_threshold = parsed_seconds
    if seconds_threshold is not None:
        now = datetime.now(timezone.utc)
        age_seconds = (now - msg.created_at).total_seconds()
        ok_age = age_seconds > seconds_threshold
        trace.append(("created_at_age_seconds", ok_age,
                      f"required>{seconds_threshold}s actual={age_seconds:.3f}s"))
        if not ok_age:
            passed = False
    else:
        trace.append(("created_at_age_seconds", True, "no threshold configured"))

    return passed, trace


# =========================
# Discord Client
# =========================
class DiscordCleanupClient(discord.Client):
    def __init__(self, patterns_content, patterns_embed, delete_conditions, mode, scan_limit, once, debug, channel_id, config, *args, **kwargs):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents, *args, **kwargs)
        self.patterns_content = patterns_content
        self.patterns_embed = patterns_embed
        self.delete_conditions = delete_conditions
        self.mode = mode
        self.scan_limit = scan_limit
        self.once = once
        self.debug = debug
        self.channel_id = channel_id
        self.config = config

    async def on_ready(self):
        print(f"[cleanup] Logged in as {self.user} (id: {self.user.id}) mode={self.mode}")
        if not self.channel_id:
            print("[cleanup][ERROR] CHANNEL_ID not configured. Stopping.")
            await self.close()
            return

        channel = self.get_channel(self.channel_id)
        if channel is None:
            print(f"[cleanup][ERROR] Channel id={self.channel_id} not found.")
            await self.close()
            return

        print("[DEBUG] on_ready: Memulai task log_cleanup_config_periodically...")
        task = asyncio.create_task(self.log_cleanup_config_periodically(interval_minutes=5))

        def task_done(t):
            if t.exception():
                print(f"[CRITICAL] Task log_cleanup_config_periodically gagal: {t.exception()}")
        task.add_done_callback(task_done)

        await self._scan_loop(channel)

    async def log_cleanup_config_periodically(self, interval_minutes=60):
        """Cetak ulang konfigurasi cleanup setiap X menit."""
        print("[DEBUG] log_cleanup_config_periodically: Loop dimulai")
        while True:
            try:
                # ✅ Ambil dari self.delete_conditions lebih dulu
                delete_conditions = self.delete_conditions or self.config.get("delete_conditions") or self.config.get("discord_delete_filters") or {}
                if not delete_conditions:
                    print("[INFO] log_cleanup_config_periodically: Tidak ada delete_conditions untuk ditampilkan")
                    await asyncio.sleep(interval_minutes * 60)
                    continue

                author = delete_conditions.get("author", "unknown")
                channel_name = delete_conditions.get("channel_name", "").lstrip("#")
                guild = delete_conditions.get("guild_name", "unknown")
                status = delete_conditions.get("status_content", "unknown")
                age = delete_conditions.get("created_at_older_than", "unknown")
                age_human = self.humanize_duration(age) if age != "unknown" else "unknown"

                now = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
                print(f"[INFO] [CLEANUP REFRESH] {now} WIB | CONFIGURED - DISCORD CLEANUP MODE: "
                      f"Bot: {author} → channel: #{channel_name} → server (guild): {guild} → "
                      f"status: {status} → Hanya hapus pesan lebih lama dari: {age_human}")

            except Exception as e:
                print(f"[ERROR] log_cleanup_config_periodically: Gagal cetak ulang konfigurasi cleanup: {e}")
                import traceback
                traceback.print_exc()

            await asyncio.sleep(interval_minutes * 60)

    def humanize_duration(self, value):
        if value is None:
            return "unknown"
        try:
            s = str(value).strip().lower()
            m = re.match(r"^(\d+(\.\d+)?)([smhd])?$", s)
            if m:
                num = float(m.group(1))
                unit = (m.group(3) or "s").lower()
                unit_map = {"s": "detik", "m": "menit", "h": "jam", "d": "hari"}
                return f"{int(num)} {unit_map.get(unit, unit)}"
        except Exception as e:
            print(f"[ERROR] humanize_duration gagal: {e}")
        return str(value)

    async def _scan_loop(self, channel):
        while True:
            if self.debug:
                print(f"[cleanup] Scanning #{channel.name} limit={self.scan_limit}")

            async for msg in channel.history(limit=self.scan_limit, oldest_first=True):
                content_text = (msg.content or "").strip()
                matched_content = detect_pattern(content_text, self.patterns_content, "KNOWN_PATTERNS_CONTENT") if content_text else {"status": "unrecognized", "pattern_source": "UNKNOWN"}

                matched_embed = {"status": "unrecognized", "pattern_source": "UNKNOWN"}
                if msg.embeds:
                    for e in msg.embeds:
                        parts = []
                        if e.title: parts.append(e.title)
                        if e.description: parts.append(e.description)
                        for field in e.fields:
                            parts.append(f"{field.name} {field.value}")
                        embed_text = "\n".join(parts).strip()
                        if embed_text:
                            r = detect_pattern(embed_text, self.patterns_embed, "KNOWN_PATTERNS_EMBED")
                            if r.get("status") == "recognized":
                                matched_embed = r
                                break

                status_info = matched_content if matched_content.get("status") == "recognized" else matched_embed
                passed, trace = check_delete_conditions_with_trace(msg, status_info, self.delete_conditions)

                if self.debug:
                    print(f"\n[MSG] id={msg.id} author={msg.author} bot={msg.author.bot}")
                    for step, ok, note in trace:
                        print(f"  - {step:20} => {'OK' if ok else 'FAIL'} -- {note}")

                if passed:
                    if self.mode == "simulate":
                        print(f"[SIMULATE] Eligible for delete: {msg.id}")
                    else:
                        try:
                            now = datetime.now(timezone.utc)
                            elapsed_seconds = (now - msg.created_at).total_seconds()
                            if elapsed_seconds >= 60:
                                m, s = divmod(int(elapsed_seconds), 60)
                                elapsed_str = f"{m}m {s}s"
                            else:
                                elapsed_str = f"{int(elapsed_seconds)}s"

                            print(f"[EXECUTE] Deleting {msg.id} (elapsed: {elapsed_str}) ...")
                            await msg.delete()
                            print(f"[EXECUTE] Deleted {msg.id}")

                        except Exception as e:
                            print(f"[ERROR] Failed to delete {msg.id}: {e}")

            if self.once:
                await self.close()
                break
            await asyncio.sleep(30 if self.mode == "execute" else 15)


# =========================
# Runner langsung
# =========================
def _run_client_loop(discord_token, patterns_content, patterns_embed, delete_conditions, mode, scan_limit, once, debug, channel_id, config):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = DiscordCleanupClient(
        patterns_content=patterns_content,
        patterns_embed=patterns_embed,
        delete_conditions=delete_conditions,
        mode=mode,
        scan_limit=scan_limit,
        once=once,
        debug=debug,
        channel_id=channel_id,
        config=config
    )
    loop.run_until_complete(client.start(discord_token))


def start_cleanup_thread(config):
    print(
        f"[DEBUG] start_cleanup_thread params: DISCORD_TOKEN set={'yes' if bool(config.get('DISCORD_TOKEN')) else 'no'}, "
        f"CHANNEL_ID={config.get('CHANNEL_ID')}, CLEANUP_MODE={config.get('CLEANUP_MODE')}, "
        f"SCAN_LIMIT={config.get('SCAN_LIMIT')}, DEBUG={config.get('CLEANUP_DEBUG')}"
    )

    patterns_content, patterns_embed, delete_conditions = load_config(config)

    _run_client_loop(
        config.get("DISCORD_TOKEN"),
        patterns_content,
        patterns_embed,
        delete_conditions,
        config.get("CLEANUP_MODE", "simulate"),
        config.get("SCAN_LIMIT", 50),
        config.get("CLEANUP_ONCE", False),
        config.get("CLEANUP_DEBUG", False),
        config.get("CHANNEL_ID"),
        config
    )
