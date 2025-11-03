# Simple Alarm Reminder

A lightweight command-line alarm tool with natural language time input. Set alarms with simple text commands like `7am`, `2:30pm`, or `in 5 minutes`.

## Quick Start

### Interactive Mode (No Arguments)
```bash
simple-alarm
```

Then just type simple commands:
- `7am` — Set alarm for 7 AM
- `2:30pm` — Set alarm at 2:30 PM  
- `in 30 seconds` — Alarm after 30 seconds
- `5 minutes with reminder` — Alarm in 5 minutes with custom message
- `quit` — Exit the program

### Command Line Mode
Run a single alarm directly:
```bash
# Alarm in 10 seconds
simple-alarm 10 seconds

# Alarm at 2:30 PM with message
simple-alarm 2:30pm with Take Medicine

# Alarm in 3 minutes
simple-alarm 3 minutes
```

## Supported Time Formats

### Absolute Times (Today or Tomorrow)
- `7am` or `7 am`
- `2:30pm` or `2:30 pm`
- `9:15am` or `9:15 am`

### Relative Times
- `in 30 seconds` or `30 seconds`
- `in 5 minutes` or `5 minutes`
- `in 2 hours` or `2 hours`

### With Custom Message
Add any message after `with`:
- `7am with take medicine`
- `in 5 minutes with break time`
- `2:30pm with meeting reminder`

## Features

✅ **Simple Input** — Just type natural language time  
✅ **Visual Alert** — Alert dialog box (macOS)  
✅ **Sound Alarm** — System beep and alarm sounds  
✅ **Notifications** — Desktop popups with reminders  
✅ **Custom Messages** — Add reminder text  
✅ **Interactive Mode** — Continuous alarm scheduling  
✅ **Command Line Mode** — Single alarm from terminal  

## Examples

```bash
# Set multiple alarms interactively
simple-alarm

# Set alarm for tomorrow at 7 AM with breakfast reminder
simple-alarm 7am with breakfast

# Alarm in 2 hours
simple-alarm 2 hours

# Alarm in 30 seconds (test)
simple-alarm 30 seconds
```

## Note

If you see `ModuleNotFoundError: No module named 'pyobjus'`, it's non-fatal. The script falls back to terminal and AppleScript notifications. To avoid the warning, install optional macOS support:
```bash
pip install pyobjus
```

## Installation

Install the package once and the `simple-alarm` command becomes available globally:
```bash
# From the project directory
pip install -e .

# Verify it works
simple-alarm 5 seconds
```
