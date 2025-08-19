import os
from datetime import datetime

APP_LIST_FILE = "logs/app_list.txt"
LOG_FILE = "logs/detected.log"

def ensure_dirs():
    if not os.path.exists("logs"):
        os.makedirs("logs")

def load_previous_list():
    ensure_dirs()
    if not os.path.exists(APP_LIST_FILE):
        return []
    apps = []
    with open(APP_LIST_FILE, "r") as f:
        for line in f.readlines():
            pkg, path = line.strip().split("::")
            apps.append((pkg, path))
    return apps

def save_current_list(apps):
    ensure_dirs()
    with open(APP_LIST_FILE, "w") as f:
        for pkg, path in apps:
            f.write(pkg + "::" + path + "\n")

def save_log(message):
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, "a") as f:
        f.write(full_message + "\n")
