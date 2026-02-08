import shutil
import os

USERS_FILE = "etc/users.json"
USERS_BAK = "etc/users.json.bak"

REPOS_DIR = "repos"
PACKAGES_DIR = "packages"
PACKAGES_BAK_DIR = "packages_backup"

def backup_users():
    if os.path.exists(USERS_FILE):
        shutil.copy2(USERS_FILE, USERS_BAK)
        print("[BACKUP] users.json backup done")

def backup_packages():
    os.makedirs(PACKAGES_BAK_DIR, exist_ok=True)
    for f in os.listdir(PACKAGES_DIR):
        src = os.path.join(PACKAGES_DIR, f)
        dst = os.path.join(PACKAGES_BAK_DIR, f)
        shutil.copy2(src, dst)
    print("[BACKUP] packages backup done")
