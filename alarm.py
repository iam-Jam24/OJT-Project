#!/usr/bin/env python3
"""
Unified natural-language alarm CLI.

Usage (all modes, single command):

  alarm 5s                        → alarm in 5 seconds
  alarm 10m wake me               → alarm in 10 minutes, message "wake me"
  alarm 2:30pm meeting            → alarm at 2:30 PM, message "meeting"
  alarm 7am wake up               → alarm at 7 AM, message "wake up"

  remind 15m take medicine        → same as alarm, "remind" keyword
  remind me 3pm meeting           → remind at 3 PM

  schedule daily 9am standup      → add a daily recurring job at 9 AM
  schedule weekly 2026-05-05T09:00:00 report → add a weekly job
  schedule once 2026-12-25T08:00:00 christmas → run once
  schedule every 300              → run every 300 seconds (interval)

  alarm list                      → list scheduled jobs
  alarm start                     → start the scheduler

  alarm                           → interactive mode (type commands at prompt)
"""

import re
import sys
import datetime
import time as time_mod

from scheduler.notifications import (
    notify_alarm_ringing,
    show_popup_notification,
)


# ──────────────────────────────────────────────────────────────
# Time parsing
# ──────────────────────────────────────────────────────────────

def parse_time_token(token: str) -> int | None:
    """
    Try to parse a single token as a duration or absolute time.
    Returns seconds (int) or None if not matched.
    Supported shorthand: 5s, 10m, 2h
    """
    token = token.lower().strip()

    # Shorthand durations: 5s, 10m, 2h
    m = re.fullmatch(r'(\d+)([smh])', token)
    if m:
        val, unit = int(m.group(1)), m.group(2)
        return val * {'s': 1, 'm': 60, 'h': 3600}[unit]

    # Absolute AM/PM: 7am, 2:30pm, 9:15am
    m = re.fullmatch(r'(\d{1,2})(?::(\d{2}))?(am|pm)', token)
    if m:
        hour, minute, ampm = int(m.group(1)), int(m.group(2) or 0), m.group(3)
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
        return _seconds_until(hour, minute)

    # 24-hour HH:MM or HH:MM:SS
    m = re.fullmatch(r'(\d{1,2}):(\d{2})(?::\d{2})?', token)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        return _seconds_until(hour, minute)

    return None


def parse_natural_phrase(words: list[str]) -> tuple[int, str, list[str]]:
    """
    Scan a word list for a time expression and return
    (seconds, time_description, remaining_words).
    Handles:
      - single token: 5s, 10m, 2h, 7am, 2:30pm
      - two tokens: "in 5 minutes", "in 2 hours", "30 seconds", "5 minutes"
    """
    i = 0
    while i < len(words):
        w = words[i].lower()

        # Skip filler words
        if w in ('in', 'at', 'for', 'me', 'a', 'an'):
            i += 1
            continue

        # Try single-token shorthand (5s / 10m / 2h / 7am / 2:30pm)
        secs = parse_time_token(w)
        if secs is not None:
            rest = words[:i] + words[i+1:]
            return secs, _fmt_secs(secs), rest

        # Try two-token relative: "5 minutes", "2 hours", "30 seconds"
        if i + 1 < len(words):
            next_w = words[i+1].lower().rstrip('s')  # strip trailing 's'
            if next_w in ('second', 'minute', 'hour') and words[i].isdigit():
                val = int(words[i])
                mult = {'second': 1, 'minute': 60, 'hour': 3600}[next_w]
                secs = val * mult
                rest = words[:i] + words[i+2:]
                return secs, _fmt_secs(secs), rest

        i += 1

    raise ValueError(
        "No time found. Examples: alarm 5s, alarm 10m lunch, alarm 7am wake up"
    )


def _seconds_until(hour: int, minute: int) -> int:
    now = datetime.datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += datetime.timedelta(days=1)
    return int((target - now).total_seconds())


def _fmt_secs(secs: int) -> str:
    if secs < 60:
        return f"{secs} second{'s' if secs != 1 else ''}"
    if secs < 3600:
        m = secs // 60
        return f"{m} minute{'s' if m != 1 else ''}"
    h = secs // 3600
    m = (secs % 3600) // 60
    return f"{h}h {m}m" if m else f"{h} hour{'s' if h != 1 else ''}"


# ──────────────────────────────────────────────────────────────
# Alarm runner
# ──────────────────────────────────────────────────────────────

def run_alarm(seconds: int, message: str, label: str = "Alarm"):
    """Count down and fire the alarm."""
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    fire_str = (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).strftime("%H:%M:%S")

    print(f"\n  ⏰  {label}")
    print(f"  📝  {message}")
    print(f"  🕐  Set at {now_str}  →  rings at {fire_str}")
    print(f"  ⏳  Counting down {_fmt_secs(seconds)} ...\n")

    show_popup_notification(
        title=f"⏰ {label} set",
        message=f"Rings in {_fmt_secs(seconds)}\n{message}",
        timeout=3,
    )

    try:
        for i in range(seconds, 0, -1):
            m, s = divmod(i, 60)
            h, m = divmod(m, 60)
            if h:
                ts = f"{h:02d}:{m:02d}:{s:02d}"
            else:
                ts = f"{m:02d}:{s:02d}"
            sys.stdout.write(f"\r  🔔  {ts} remaining ...   ")
            sys.stdout.flush()
            time_mod.sleep(1)

        print("\n\n" + "  " + "─" * 50)
        print("  🔔🔔🔔  DING DONG — ALARM!  🔔🔔🔔")
        print("  " + "─" * 50 + "\n")

        notify_alarm_ringing(label, duration=6)
        show_popup_notification(
            title=f"🔔 {label}",
            message=message,
            timeout=6,
        )
        print(f"  ✓  {message}\n")

    except KeyboardInterrupt:
        print("\n\n  👋  Alarm cancelled.\n")
        sys.exit(0)


# ──────────────────────────────────────────────────────────────
# Schedule sub-command (wraps scheduler-cli engine)
# ──────────────────────────────────────────────────────────────

def run_schedule(words: list[str]):
    """
    Natural language scheduling:
      schedule daily 9am standup
      schedule weekly 2026-05-05T09:00:00 report
      schedule once 2026-12-25T08:00:00 christmas
      schedule every 300
      schedule every 5m check
    """
    from scheduler.engine import SchedulerEngine

    if not words:
        print("Usage: alarm schedule <freq> <time> [name]\n"
              "  alarm schedule daily 9am standup\n"
              "  alarm schedule every 5m check\n"
              "  alarm schedule once 2026-12-25T08:00:00 christmas")
        return

    freq = words[0].lower()
    rest = words[1:]

    engine = SchedulerEngine()

    if freq == "every":
        # schedule every 300 / every 5m
        if not rest:
            print("  ❌  Specify interval: alarm schedule every 300  or  alarm schedule every 5m")
            return
        secs = parse_time_token(rest[0])
        if secs is None:
            if rest[0].isdigit():
                secs = int(rest[0])
            else:
                print(f"  ❌  Cannot parse interval '{rest[0]}'. Use seconds (300) or shorthand (5m).")
                return
        job_name = " ".join(rest[1:]) if len(rest) > 1 else f"every_{secs}s"
        rule = {"frequency": "interval", "seconds": secs}
        engine.add_job(job_name, "echo task", rule)
        print(f"  ✅  Job '{job_name}' scheduled every {_fmt_secs(secs)}")
        return

    if freq not in ("once", "daily", "weekly", "hourly"):
        print(f"  ❌  Unknown frequency '{freq}'. Use: daily, weekly, once, hourly, every")
        return

    if not rest:
        print(f"  ❌  Provide a time: alarm schedule {freq} 9am standup")
        return

    time_str = rest[0]
    job_name = " ".join(rest[1:]) if len(rest) > 1 else f"{freq}_job"

    # Accept shorthand like 9am -> convert to ISO
    if not re.match(r'\d{4}-\d{2}-\d{2}T', time_str):
        secs = parse_time_token(time_str)
        if secs is None:
            print(f"  ❌  Cannot parse time '{time_str}'. Use 9am / 14:30 / 2026-12-25T09:00:00")
            return
        target_dt = datetime.datetime.now() + datetime.timedelta(seconds=secs)
        time_str = target_dt.strftime("%Y-%m-%dT%H:%M:%S")

    rule = {"frequency": freq, "time": time_str}
    engine.add_job(job_name, "echo task", rule)
    print(f"  ✅  Job '{job_name}' ({freq}) scheduled at {time_str}")


# ──────────────────────────────────────────────────────────────
# Interactive mode
# ──────────────────────────────────────────────────────────────

def interactive_mode():
    print("\n" + "  " + "═" * 54)
    print("  🔔  ALARM  —  type a command or 'help'")
    print("  " + "═" * 54)
    print("  Examples:")
    print("    5s                   alarm in 5 seconds")
    print("    10m wake me          alarm in 10 minutes")
    print("    7am good morning     alarm at 7 AM")
    print("    2:30pm meeting       alarm at 2:30 PM")
    print("    remind 30m lunch     remind me in 30 min")
    print("    quit / exit          leave")
    print("  " + "─" * 54 + "\n")

    while True:
        try:
            raw = input("  ▶  ").strip()
            if not raw:
                continue
            if raw.lower() in ("quit", "exit", "q"):
                print("  👋  Goodbye!\n")
                break
            if raw.lower() == "help":
                print("  alarm 5s / 10m / 2h / 7am / 2:30pm [message]")
                print("  schedule daily 9am standup")
                print("  schedule every 5m check\n")
                continue
            process_command(raw.split())
        except KeyboardInterrupt:
            print("\n  👋  Goodbye!\n")
            break


# ──────────────────────────────────────────────────────────────
# Command dispatcher
# ──────────────────────────────────────────────────────────────

def process_command(words: list[str]):
    if not words:
        return

    cmd = words[0].lower()

    # ── list / start (scheduler passthrough) ──────────────────
    if cmd == "list":
        from scheduler.engine import SchedulerEngine
        jobs = SchedulerEngine().list_jobs()
        if not jobs:
            print("  (no scheduled jobs)")
        else:
            for j in jobs:
                print(f"  • {j['name']}  |  next: {j['next_run']}")
        return

    if cmd == "start":
        print("  Starting scheduler ... (Ctrl+C to stop)")
        from scheduler.engine import SchedulerEngine
        engine = SchedulerEngine()
        engine.start()
        try:
            while True:
                time_mod.sleep(1)
        except KeyboardInterrupt:
            engine.stop()
            print("\n  Scheduler stopped.")
        return

    # ── schedule ───────────────────────────────────────────────
    if cmd in ("schedule", "sched"):
        run_schedule(words[1:])
        return

    # ── alarm / remind / remind me → strip keyword, parse rest ─
    rest = words[:]
    if cmd in ("alarm", "remind", "reminder"):
        rest = words[1:]
    if rest and rest[0].lower() == "me":
        rest = rest[1:]

    if not rest:
        interactive_mode()
        return

    # Parse time + message from the remaining words
    try:
        secs, time_desc, leftover = parse_natural_phrase(rest)
    except ValueError as e:
        print(f"  ❌  {e}")
        return

    # Everything left over is the message
    message = " ".join(leftover).strip() or "Alarm"
    label = f"Alarm in {time_desc}"

    run_alarm(secs, message, label)


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        interactive_mode()
    else:
        process_command(sys.argv[1:])


if __name__ == "__main__":
    main()
