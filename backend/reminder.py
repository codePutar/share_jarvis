import time
import datetime
import threading
from TextToSpeech_v4 import TTS

# Fixed daily reminders
BREAK_INTERVAL = 30 * 60  # 30 minutes in seconds
BED_TIME = "23:00"        # 11:00 PM
MORNING_GREETING_TIME = "06:00"

last_break_time = time.time()
greeted_today = False

# Storage for custom reminders
custom_reminders = []  # Each item: {"time": datetime, "message": str, "repeat": None or seconds}

def add_custom_reminder(reminder_time, message, repeat_interval=None):
    """Add a custom reminder."""
    custom_reminders.append({
        "time": reminder_time,
        "message": message,
        "repeat": repeat_interval
    })
    TTS(f"Reminder set for {reminder_time.strftime('%I:%M %p')} with message: {message}")

def check_break():
    global last_break_time
    if time.time() - last_break_time >= BREAK_INTERVAL:
        TTS("Hey! It's time to take a break. Stretch, walk, or relax your eyes.")
        last_break_time = time.time()

def check_bedtime():
    current_time = datetime.datetime.now().strftime("%H:%M")
    if current_time == BED_TIME:
        TTS("It's bedtime now. Please go to sleep for a fresh start tomorrow.")

def check_morning_greeting():
    global greeted_today
    current_time = datetime.datetime.now().strftime("%H:%M")
    if not greeted_today and current_time >= MORNING_GREETING_TIME:
        TTS("Good morning! Let's make today productive and amazing.")
        greeted_today = True

def check_custom_reminders():
    now = datetime.datetime.now()
    for reminder in list(custom_reminders):
        if now >= reminder["time"]:
            TTS(reminder["message"])
            if reminder["repeat"]:
                reminder["time"] = now + datetime.timedelta(seconds=reminder["repeat"])
            else:
                custom_reminders.remove(reminder)

def reminder_loop():
    TTS("Reminder system started.")
    while True:
        check_break()
        check_bedtime()
        check_morning_greeting()
        check_custom_reminders()
        time.sleep(30)  # Check every 30 seconds

# Example parser for your "reminder" command
def parse_reminder_command(command_str):
    """
    Examples it can parse:
    - remind me to drink water every 1 hour
    - set a reminder at 3:30pm to call mom
    - remind me in 15 minutes to check the oven
    """
    command_str = command_str.lower()
    now = datetime.datetime.now()

    if "every" in command_str:  # Repeat reminder
        parts = command_str.split("every")
        message = parts[0].replace("remind me to", "").strip()
        time_part = parts[1].strip()

        if "hour" in time_part:
            interval = int(time_part.split()[0]) * 3600
        elif "minute" in time_part:
            interval = int(time_part.split()[0]) * 60
        else:
            interval = 3600  # Default 1 hour

        add_custom_reminder(now + datetime.timedelta(seconds=interval), message, repeat_interval=interval)

    elif "in" in command_str:  # Reminder after some time
        parts = command_str.split("in")
        message = parts[1].split("to")[-1].strip()
        time_part = parts[1].split("to")[0].strip()

        if "hour" in time_part:
            delay = int(time_part.split()[0]) * 3600
        elif "minute" in time_part:
            delay = int(time_part.split()[0]) * 60
        else:
            delay = 60

        add_custom_reminder(now + datetime.timedelta(seconds=delay), message)

    elif "at" in command_str:  # Specific time reminder
        parts = command_str.split("at")
        time_part = parts[1].split("to")[0].strip()
        message = parts[1].split("to")[-1].strip()

        reminder_time = datetime.datetime.strptime(time_part, "%I:%M%p").replace(
            year=now.year, month=now.month, day=now.day
        )
        if reminder_time < now:
            reminder_time += datetime.timedelta(days=1)  # If time already passed today

        add_custom_reminder(reminder_time, message)

if __name__ == "__main__":
    threading.Thread(target=reminder_loop, daemon=True).start()
    # Test commands
    parse_reminder_command("remind me in 1 minute to stretch")
    while True:
        time.sleep(1)
