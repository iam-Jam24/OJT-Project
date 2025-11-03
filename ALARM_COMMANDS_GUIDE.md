# ⏰ Alarm Commands Guide

One command for everything: `alarm`. No flags, no `python3`, just plain English.

---

## ⚡ Quick Start (TL;DR)

```bash
alarm 5s                      # alarm in 5 seconds
alarm 10m wake me             # alarm in 10 min, message "wake me"
alarm 7am good morning        # alarm at 7 AM
alarm 2:30pm team meeting     # alarm at 2:30 PM

remind 15m take medicine      # same as alarm — "remind" also works
remind me 1h lunch            # "remind me" works too

alarm schedule daily 9am standup    # recurring daily job
alarm schedule every 5m check       # every 5 minutes

alarm list                    # show all scheduled jobs
alarm start                   # start the scheduler
alarm                         # interactive mode (type commands)
```

---

## 🔔 `alarm` — Natural Language Alarm

### Syntax
```
alarm <time> [message]
alarm <time> [message]
remind <time> [message]
remind me <time> [message]
```

### Time formats you can use

| You type | Meaning |
|----------|---------|
| `5s` | 5 seconds |
| `10m` | 10 minutes |
| `2h` | 2 hours |
| `7am` | 7:00 AM (tomorrow if already past) |
| `9:15am` | 9:15 AM |
| `2:30pm` | 2:30 PM |
| `14:30` | 2:30 PM (24-hour) |
| `30 seconds` | 30 seconds (word form) |
| `5 minutes` | 5 minutes (word form) |

### Examples

```bash
# ── seconds ──────────────────────────────────────────────────
alarm 5s                          # alarm in 5 seconds
alarm 30s check the oven          # 30 seconds, "check the oven"

# ── minutes ──────────────────────────────────────────────────
alarm 10m                         # 10 minutes
alarm 30m time for a break        # 30 minutes with message
remind 15m take medicine          # "remind" works the same way

# ── hours ────────────────────────────────────────────────────
alarm 1h                          # 1 hour
alarm 2h review emails            # 2 hours with message

# ── specific time ─────────────────────────────────────────────
alarm 7am wake up                 # 7 AM
alarm 9:15am morning standup      # 9:15 AM
alarm 2pm team meeting            # 2:00 PM
alarm 2:30pm take medicine        # 2:30 PM

# ── "remind me" style ─────────────────────────────────────────
remind me 10m stretch             # 10 minutes
remind me 3pm meeting             # 3 PM

# ── word form ─────────────────────────────────────────────────
alarm 30 seconds test             # word-style seconds
alarm 5 minutes lunch             # word-style minutes
```

### What happens when it rings
1. Countdown shows in terminal (`MM:SS`)
2. Desktop notification pops up
3. **🔔 DING DONG** doorbell sound plays (Glass + Pop tones)
4. Alert dialog appears
5. Press **Ctrl+C** at any time to cancel

---

## 📅 `alarm schedule` — Recurring Jobs

### Syntax
```
alarm schedule <frequency> <time> [name]
```

### Frequencies

| Command | Meaning |
|---------|---------|
| `alarm schedule daily 9am standup` | Every day at 9 AM |
| `alarm schedule weekly 2026-05-05T09:00:00 report` | Every week |
| `alarm schedule once 2026-12-25T08:00:00 christmas` | Run once |
| `alarm schedule hourly 00:00:00 check` | Every hour |
| `alarm schedule every 300` | Every 300 seconds |
| `alarm schedule every 5m check` | Every 5 minutes |

### Examples

```bash
# Every day at 9 AM
alarm schedule daily 9am morning-standup

# Every 5 minutes
alarm schedule every 5m server-check

# Every 30 seconds
alarm schedule every 30s heartbeat

# Run once at a specific date/time
alarm schedule once 2026-12-25T09:00:00 christmas-alarm

# Weekly on the same day
alarm schedule weekly 2026-05-05T17:00:00 friday-report
```

### Manage jobs

```bash
alarm list          # show all scheduled jobs
alarm start         # start running scheduled jobs (Ctrl+C to stop)
```

---

## 🗣️ Interactive Mode

Run `alarm` with no arguments for an interactive prompt:

```bash
alarm
```

Then type commands at the prompt:
```
  ▶  5s                    → alarm in 5 seconds
  ▶  10m wake me           → alarm in 10 min
  ▶  7am good morning      → alarm at 7 AM
  ▶  2:30pm meeting        → alarm at 2:30 PM
  ▶  schedule daily 9am    → recurring daily job
  ▶  list                  → show scheduled jobs
  ▶  quit                  → exit
```

---

## 🔁 All Commands at a Glance

| What you want | Command |
|---------------|---------|
| Alarm in 5 seconds | `alarm 5s` |
| Alarm in 10 min with message | `alarm 10m wake me` |
| Alarm at 2:30 PM | `alarm 2:30pm meeting` |
| Remind in 15 min | `remind 15m take medicine` |
| Remind me in 1 hour | `remind me 1h lunch` |
| Daily job at 9 AM | `alarm schedule daily 9am standup` |
| Every 5 minutes | `alarm schedule every 5m check` |
| Run once on a date | `alarm schedule once 2026-12-25T09:00:00 christmas` |
| View scheduled jobs | `alarm list` |
| Start scheduler | `alarm start` |
| Interactive mode | `alarm` |

---

## 💡 Tips

- All times auto-schedule for **tomorrow** if already past today
- `remind` is an alias — `remind 10m lunch` = `alarm 10m lunch`
- Press **Ctrl+C** to cancel any running alarm
- Scheduled jobs are saved to `jobs.json` and persist between runs
- Add a shell alias for even shorter typing:
  ```bash
  # In ~/.zshrc or ~/.bashrc
  alias a='alarm'
  ```
  Then: `a 10m coffee`

---

## 🛠️ Setup (One Time)

```bash
cd /Users/iamjam01/Desktop/OJT-Project-2
pip install -e .
```

After that, `alarm` and `remind` are available everywhere — no `python3` needed.
