#!/usr/bin/env python3
import os, sys, json, subprocess, getpass, uuid, shutil
from groups.manager import groupadd, grouplist, groupsettings
import readline
from groups.chat import group_send, flush_queue
# =========================
# ROOT & PATH
# =========================
ROOT = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(ROOT, "bin")
USR_BIN = os.path.join(ROOT, "usr", "bin")
ETC = os.path.join(ROOT, "etc")
HOME_BASE = os.path.join(ROOT, "home")
LOCK_DIR = os.path.join(ETC, "locks")

os.makedirs(LOCK_DIR, exist_ok=True)
os.makedirs(HOME_BASE, exist_ok=True)

os.environ["PATH"] = f"{BIN}:{USR_BIN}:" + os.environ.get("PATH", "")

USERS_DB = os.path.join(ETC, "users.json")


PERM_DB = os.path.join(ETC, "permissions.json")

if not os.path.exists(PERM_DB):
    json.dump({"/": {"owner": "root", "perm": "rwx"}}, open(PERM_DB, "w"), indent=2)

PERMS = json.load(open(PERM_DB))

def save_perms():
    json.dump(PERMS, open(PERM_DB, "w"), indent=2)

def has_perm(path, mode):
    if IS_ROOT:
        return True
    meta = PERMS.get(path)
    if not meta:
        return True  # default allow
    if meta["owner"] == USERNAME:
        return mode in meta["perm"]
    return False


# =========================
# INIT DATABASE
# =========================
if not os.path.exists(USERS_DB):
    with open(USERS_DB, "w") as f:
        json.dump({
            "root": {
                "username": "root",
                "password": "root",
                "uuid": "0",
                "role": "root",
                "home": "/"
            }
        }, f, indent=2)

# =========================
# UTIL
# =========================
def save_users():
    json.dump(USERS, open(USERS_DB, "w"), indent=2)

try:
    with open(USERS_DB) as f:
        USERS = json.load(f)
except json.JSONDecodeError:
    print("[WARN] users.json corrupt, regenerating...")
    USERS = {
        "root": {
            "username": "root",
            "password": "root",
            "uuid": "0",
            "uid": 0,
            "gid": 0,
            "groups": ["root"],
            "role": "root",
            "home": "/",
            "shell": "/bin/neosh",
            "umask": "022"
        }
    }
    with open(USERS_DB, "w") as f:
        json.dump(USERS, f, indent=2)

changed = False
for u, data in USERS.items():
    if "uid" not in data:
        data["uid"] = 0 if u == "root" else next_uid()
        changed = True
    if "gid" not in data:
        data["gid"] = data["uid"]
        changed = True
    if "groups" not in data:
        data["groups"] = [u]
        changed = True
    if "shell" not in data:
        data["shell"] = "/bin/neosh"
        changed = True
    if "umask" not in data:
        data["umask"] = "022"
        changed = True

if changed:
    save_users()

def next_uid():
    used = [u.get("uid", 0) for u in USERS.values()]
    return max(used, default=999) + 1

def is_user_logged_in(username):
    return os.path.exists(os.path.join(LOCK_DIR, f"{username}.lock"))

def set_user_logged_in(username):
    open(os.path.join(LOCK_DIR, f"{username}.lock"), "w").close()

def set_user_logged_out(username):
    f = os.path.join(LOCK_DIR, f"{username}.lock")
    if os.path.exists(f):
        os.remove(f)

# =========================
# CENTERED LOGIN
# =========================
def centered_login():
    os.system("clear")
    cols, rows = shutil.get_terminal_size((80, 24))
    lines = [
        "=" * 40,
        "        Welcome to NeoTermOS        ",
        "=" * 40,
        "",
        "           Please login             ",
        ""
    ]
    print("\n" * ((rows - len(lines)) // 2))
    for l in lines:
        print(l.center(cols))

# =========================
# LOGIN
# =========================
def login():
    centered_login()
    for _ in range(3):
        u = input("username: ").strip()
        p = getpass.getpass("password: ")
        user = USERS.get(u)
        if user and user["password"] == p:
            if is_user_logged_in(u):
                print("[LOGIN] User already logged in ❌")
                continue
            set_user_logged_in(u)
            return user
        print("Login incorrect\n")
    sys.exit(1)

CURRENT_USER = login()
USERNAME = CURRENT_USER["username"]
IS_ROOT = CURRENT_USER["role"] == "root"

# =========================
# INIT VFS
# =========================
from vfs.vfs import VFS
from pkg.neopkg import NeoPkg

HOME_PATH = CURRENT_USER.get("home", "/")

if HOME_PATH != "/":
    REAL_HOME = os.path.join(ROOT, HOME_PATH.strip("/"))
    os.makedirs(REAL_HOME, exist_ok=True)
else:
    REAL_HOME = ROOT

vfs = VFS(
    ROOT,
    HOME_PATH,
    uid=CURRENT_USER["uid"],
    gid=CURRENT_USER["gid"],
    is_root=IS_ROOT
)
vfs.cd(HOME_PATH)

neopkg = NeoPkg(ROOT)

def load_profile():
    if HOME_PATH == "/":
        return
    profile = os.path.join(REAL_HOME, ".profile")
    if not os.path.exists(profile):
        with open(profile, "w") as f:
            f.write("# ~/.profile\n")
            f.write("echo 'Login successful'\n")
    with open(profile) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                exec_cmd(line)

# =========================
# LOAD ~/.neorc
# =========================
def load_neorc():
    if HOME_PATH == "/":
        return
    neorc = os.path.join(REAL_HOME, ".neorc")
    if not os.path.exists(neorc):
        with open(neorc, "w") as f:
            f.write("# ~/.neorc\n")
            f.write("echo 'Welcome to NeoTermOS'\n")
    with open(neorc) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                exec_cmd(line)

# =========================
# PROMPT
# =========================
def prompt():
    sym = "#" if IS_ROOT else "$"
    return f"NeoTermOS:{USERNAME}{sym}{vfs.pwd()} "

# =========================
# EXEC & SUDO
# =========================
def exec_cmd(cmd):
    env = os.environ.copy()
    env["PATH"] = f"{BIN}:{USR_BIN}:" + env.get("PATH", "")
    subprocess.run(cmd, shell=True, env=env)

def sudo_exec(cmd):
    if IS_ROOT:
        exec_cmd(cmd)
        return
    pw = getpass.getpass("[sudo] password for root: ")
    if pw != USERS["root"]["password"]:
        print("Wrong password")
        return
    exec_cmd(cmd)

print("\033[1;32mNeoTermOS — Kernel Online\033[0m")

load_profile()
load_neorc()


# di main loop sebelum input prompt
for g in CURRENT_USER.get("groups", []):
    flush_queue(g, USERNAME)
# =========================
# MAIN SHELL LOOP
# =========================
while True:
    try:
        cmd = input(prompt()).strip()
    except (EOFError, KeyboardInterrupt):
        continue
        #break


    if not cmd:
        continue

    parts = cmd.split()

    if cmd in ("exit", "quit"):
        set_user_logged_out(USERNAME)
        break

    #elif cmd in ("cd", "cd ~"):
        #vfs.cd(HOME_PATH)

    elif cmd.startswith("cd "):
        target = cmd[3:].strip()
        if target == "~":
            vfs.cd(HOME_PATH)
        else:
            full = vfs._resolve(target)
            if not has_perm(full, "x"):
                print("Permission denied")
            else:
                vfs.cd(target)

    elif cmd == "pwd":
        print(vfs.pwd())

    elif cmd == "id":
        u = USERS[USERNAME]
        print(
            f"uid={u['uid']}({USERNAME}) "
            f"gid={u['gid']} groups={','.join(u['groups'])}"
        )

    elif cmd == "whoami":
        print(USERNAME)

    elif cmd == "ls":
        if not has_perm(vfs.pwd(), "r"):
            print("Permission denied")
        else:
            for f in vfs.ls():
                print(f)

    elif parts[0] == "sudo":
        sudo_exec(" ".join(parts[1:]))

    elif parts[0] == "useradd":
        if not IS_ROOT:
            print("Permission denied")
            continue

        u = input("Username: ").strip()
        if u in USERS:
            print("User already exists")
            continue

        p = getpass.getpass("Password: ")
        role = input("Role (root/user): ").strip() or "user"

        if role == "root":
            home = "/"
        else:
            home = f"/home/{u}"
            real_home = os.path.join(ROOT, home.strip("/"))
            os.makedirs(real_home, exist_ok=True)

            neorc = os.path.join(real_home, ".neorc")
            if not os.path.exists(neorc):
                with open(neorc, "w") as f:
                    f.write("# ~/.neorc\n")
                    f.write("echo 'Welcome to NeoTermOS'\n")

        uid = next_uid()
        gid = uid   # private group model (kayak Linux)

        USERS[u] = {
            "username": u,
            "password": p,
            "uuid": str(uuid.uuid4()),
            "uid": uid,
            "gid": gid,
            "groups": [u],        # default group = username
            "role": role,
            "home": home,
            "shell": "/bin/neosh",
            "umask": "022"
        }
        os.makedirs(real_home, exist_ok=True)
        PERMS[home] = {"owner": u, "perm": "rwx"}
        save_perms()
        vfs.chown(home, u)
        vfs.chmod(home, "rwx")
        save_users()
        print(f"User '{u}' created ✅")

    elif parts[0] == "deluser":
        if not IS_ROOT:
            print("Permission denied")
            continue
        u = input("Username to delete: ").strip()
        if u == "root":
            print("Cannot delete root")
        elif u in USERS:
            del USERS[u]
            save_users()
            print(f"User '{u}' deleted ✅")
        else:
            print("User not found")

    elif cmd == "userlist":
        print(f"{'Username':<15}{'UUID':<38}{'Role':<6}{'Home'}")
        for u, i in USERS.items():
            print(f"{i.get('username','-'):<15}{i.get('uuid','-'):<38}{i.get('role','-'):<6}{i.get('home','-')}")

    elif parts[0] == "neo":
        if len(parts) == 1:
            print(
                "neo add <repo>\n"
                "neo update\n"
                "neo list\n"
                "neo search <pkg>\n"
                "neo down <pkg>"
            )
        elif parts[1] == "add" and len(parts) == 3:
            neopkg.add(parts[2])
        elif parts[1] == "update":
            neopkg.update()
        elif parts[1] == "list":
            neopkg.list()
        elif parts[1] == "search" and len(parts) == 3:
            neopkg.search(parts[2])
        elif parts[1] == "down" and len(parts) == 3:
            neopkg.down(parts[2])
        else:
            print("Unknown neo command")

    elif parts[0] == "chmod":
        if not IS_ROOT:
            print("Permission denied")
            continue

        recursive = "-R" in parts

        try:
            if recursive:
                mode = parts[2]
                path = parts[3]
            else:
                mode = parts[1]
                path = parts[2]

            vpath = vfs._resolve(path)
            vfs.chmod(vpath, mode, recursive=recursive)

        except Exception as e:
             print(f"chmod error: {e}")

    elif parts[0] == "chown":
         if not IS_ROOT:
             print("Permission denied")
             continue

         recursive = "-R" in parts

         try:
             if recursive:
                 user = parts[2]
                 path = parts[3]
             else:
                 user = parts[1]
                 path = parts[2]

             if user not in USERS:
                 print("User not found")
                 continue

             uid = USERS[user]["uid"]
             gid = USERS[user]["gid"]

             vpath = vfs.resolve(path)
             vfs.chown(vpath, uid, gid, recursive=recursive)

         except Exception as e:
             print(f"chown error: {e}")

    elif parts[0] == "groupadd":
         if not IS_ROOT:
             print("Permission denied")
             continue
         if len(parts) < 2:
             print("Usage: groupadd <groupname>")
             continue
         print(groupadd(parts[1], USERNAME))

    elif parts[0] == "grouplist":
         for g in grouplist():
             print(g)

    elif parts[0] == "groupsettings":
          if len(parts) < 2:
              print("Usage: groupsettings <groupname>")
              continue
          settings = groupsettings(parts[1])
          if not settings:
              print("Group not found")
          else:
              print(json.dumps(settings, indent=2))

    elif parts[0] == "gmsg":
          if len(parts) < 3:
              print("Usage: gmsg <group> <message>")
              continue
          group_name = parts[1]
          msg = " ".join(parts[2:])
          group_send(group_name, USERNAME, msg)

    elif parts[0] == "groupadduser":
         if not IS_ROOT:
             print("Permission denied")
             continue
         if len(parts) < 3:
             print("Usage: groupadduser <username> <groupname>")
             continue
         u = parts[1]
         g = parts[2]
         if u not in USERS:
             print(f"User '{u}' not found")
             continue
    # from groups.manager import grouplist
         if g not in grouplist():
             print(f"Group '{g}' not found")
             continue
         if g in USERS[u]["groups"]:
             print(f"User '{u}' is already a member of '{g}'")
             continue
         USERS[u]["groups"].append(g)
         save_users()
         print(f"User '{u}' added to group '{g}' ✅")

    else:
        exec_cmd(cmd)
