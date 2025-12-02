"""
Notification and alarm module for scheduler jobs.
Provides pop-up notifications, system notifications, and alarm sounds.
"""

import os
import sys
import threading
import warnings
from pathlib import Path

# Suppress plyer-related warnings
warnings.filterwarnings('ignore')

try:
    from plyer import notification
except (ImportError, ModuleNotFoundError):
    notification = None


# Available system sounds on macOS
MACOS_SOUNDS = {
    "alarm": "/System/Library/Sounds/Ping.aiff",
    "bell": "/System/Library/Sounds/Glass.aiff",
    "notification": "/System/Library/Sounds/Ping.aiff",
    "alert": "/System/Library/Sounds/Sosumi.aiff",
    "beep": "/System/Library/Sounds/Tink.aiff",
    "pop": "/System/Library/Sounds/Pop.aiff",
    "success": "/System/Library/Sounds/Tink.aiff",
}


def play_notification_sound(sound_type="notification"):
    """
    Play a notification sound based on type.
    
    Args:
        sound_type (str): Type of sound - 'alarm', 'notification', 'alert', etc.
    """
    try:
        if sys.platform == "darwin":  # macOS
            sound_file = MACOS_SOUNDS.get(sound_type, MACOS_SOUNDS["notification"])
            # Play sound in background
            os.system(f"afplay {sound_file} > /dev/null 2>&1 &")
        elif sys.platform == "win32":  # Windows
            import winsound
            # Play default Windows sound
            winsound.MessageBeep()
        elif sys.platform == "linux":  # Linux
            # Use paplay or aplay if available
            os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null &")
    except Exception as e:
        pass  # Silently fail if sound unavailable


def play_alarm_sound(duration=3):
    """
    Play a system beep/alarm sound for the specified duration.
    
    Args:
        duration (int): Duration of the alarm in seconds
    """
    try:
        if sys.platform == "darwin":  # macOS
            # Play alarm sound multiple times
            for _ in range(2):
                os.system("afplay /System/Library/Sounds/Alarm.aiff > /dev/null 2>&1")
                import time as time_mod
                time_mod.sleep(0.5)
        elif sys.platform == "win32":  # Windows
            # Use Windows beep
            import winsound
            winsound.Beep(1000, int(duration * 1000))
        elif sys.platform == "linux":  # Linux
            # Use beep command or speaker-test
            os.system(f"(speaker-test -t sine -f 1000 -l 1 2>/dev/null || beep) &")
    except Exception as e:
        pass  # Silently fail if sound unavailable


def show_popup_notification(title, message, timeout=10):
    """
    Show a system pop-up notification.
    
    Args:
        title (str): Title of the notification
        message (str): Message content
        timeout (int): Timeout in seconds (default 10)
    """
    try:
        if notification:
            notification.notify(
                title=title,
                message=message,
                timeout=timeout,
                app_name="Scheduler",
            )
        else:
            print(f"\n🔔 {title}")
            print(f"   {message}")
    except Exception as e:
        # Silently fail for plyer notification - it's optional
        pass


def show_popup_window(title, message):
    """
    Show a pop-up dialog window (macOS).
    Falls back to terminal display on other systems.
    
    Args:
        title (str): Title of the dialog
        message (str): Message content
    """
    try:
        if sys.platform == "darwin":  # macOS
            # Use osascript for native macOS notification
            # Escape quotes in the message
            safe_message = message.replace('"', '\\"')
            safe_title = title.replace('"', '\\"')
            script = f'display notification "{safe_message}" with title "{safe_title}"'
            os.system(f'osascript -e \'{script}\' &')
        else:
            # Show notification through plyer
            show_popup_notification(title, message)
    except Exception as e:
        print(f"Could not show pop-up: {e}")


def notify_job_execution(job_name, with_sound=True, with_popup=True):
    """
    Comprehensive notification when a job is executed.
    
    Args:
        job_name (str): Name of the job being executed
        with_sound (bool): Whether to play alarm sound
        with_popup (bool): Whether to show pop-up notification
    """
    print(f"\n⏰ JOB ALERT: {job_name}")
    
    if with_sound:
        # Play notification sound in background thread so it doesn't block execution
        sound_thread = threading.Thread(
            target=play_notification_sound, 
            args=("alarm",),
            daemon=True
        )
        sound_thread.start()
    
    if with_popup:
        notification_thread = threading.Thread(
            target=show_popup_window,
            args=(f"Job Execution", f"Job '{job_name}' is now running"),
            daemon=True
        )
        notification_thread.start()


def notify_job_completed(job_name, next_run_time):
    """
    Notification when a job completes.
    
    Args:
        job_name (str): Name of the job
        next_run_time (str): Time of next run
    """
    message = f"Job completed. Next run: {next_run_time}"
    show_popup_notification(
        title=f"✓ {job_name} Completed",
        message=message,
        timeout=5
    )
    
    # Play a success/completion sound in background
    sound_thread = threading.Thread(
        target=play_notification_sound,
        args=("success",),
        daemon=True
    )
    sound_thread.start()


def show_alert_dialog(job_name, message=""):
    """
    Show an alert dialog box during alarm execution (macOS specific).
    Falls back to terminal display on other systems.
    
    Args:
        job_name (str): Name of the job triggering the alert
        message (str): Additional alert message
    """
    try:
        if sys.platform == "darwin":  # macOS
            # Create an interactive alert dialog
            alert_text = f"🚨 ALARM: {job_name}"
            if message:
                alert_text += f"\n\n{message}"
            
            safe_text = alert_text.replace('"', '\\"').replace("'", "\\'")
            
            # Use AppleScript to show an alert dialog
            script = f'''
            tell application "System Events"
                display alert "{job_name}" message "{message}" buttons {{"Dismiss", "Snooze"}} default button 1 with icon caution
            end tell
            '''
            os.system(f"osascript -e '{script}' > /dev/null 2>&1 &")
        else:
            # Fallback for Windows/Linux
            print(f"\n🚨 ALERT: {job_name}")
            if message:
                print(f"   {message}")
    except Exception as e:
        print(f"\n🚨 ALERT: {job_name}")
        if message:
            print(f"   {message}")


def notify_alarm_ringing(job_name, duration=5):
    """
    Comprehensive alarm notification with sound, visual alert, and popup.
    Called when an alarm job is triggered.
    
    Args:
        job_name (str): Name of the alarm job
        duration (int): Duration to play alarm sound (seconds)
    """
    print(f"\n🔔🔔🔔 ALARM RINGING: {job_name} 🔔🔔🔔")
    
    # Show alert dialog in background thread
    alert_thread = threading.Thread(
        target=show_alert_dialog,
        args=(job_name, "Your scheduled alarm has been triggered!"),
        daemon=True
    )
    alert_thread.start()
    
    # Play alarm sound in background thread
    alarm_thread = threading.Thread(
        target=play_alarm_sound,
        args=(duration,),
        daemon=True
    )
    alarm_thread.start()
    
    # Show popup notification
    popup_thread = threading.Thread(
        target=show_popup_notification,
        args=(f"⏰ {job_name}", "Alarm is ringing!", duration),
        daemon=True
    )
    popup_thread.start()
