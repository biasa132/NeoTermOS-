import os, json
from datetime import datetime

GROUPS_DIR = os.path.join(os.path.dirname(__file__))

def group_path(name):
    return os.path.join(GROUPS_DIR, name)

def group_send(name, sender, message):
    path = group_path(name)
    chat_log = os.path.join(path, "chat.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {sender}: {message}\n"

    # tulis log
    with open(chat_log, "a") as f:
        f.write(line)

    # push ke queue semua member
    members_file = os.path.join(path, "members.json")
    with open(members_file) as f:
        members = json.load(f)
    queue_dir = os.path.join(path, "queue")
    for member in members:
        if member == sender:
            continue
        queue_file = os.path.join(queue_dir, f"{member}.queue")
        with open(queue_file, "a") as f:
            f.write(line)

def flush_queue(group_name, username):
    path = group_path(group_name)
    queue_file = os.path.join(path, "queue", f"{username}.queue")
    if not os.path.exists(queue_file):
        return
    with open(queue_file) as f:
        lines = f.readlines()
    if lines:
        print("".join(lines), end="")
        open(queue_file, "w").close()
