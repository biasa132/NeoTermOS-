import os, json, uuid

GROUPS_DIR = os.path.join(os.path.dirname(__file__))
# false GROUPS_DB = os.path.join(os.path.dirname(__file__), "groups.json")

GROUPS_DB = os.path.join(os.path.dirname(__file__), "groups.json")

def load_groups():
    if not os.path.exists(GROUPS_DB):
        with open(GROUPS_DB, "w") as f:
            json.dump({}, f, indent=2)
    with open(GROUPS_DB) as f:
        return json.load(f)

def save_groups(groups):
    with open(GROUPS_DB, "w") as f:
        json.dump(groups, f, indent=2)

#def grouplist():
 #   groups = load_groups()
  #  return list(groups.keys())

def group_path(name):
    return os.path.join(GROUPS_DIR, name)

def groupadd(name, creator):
    path = group_path(name)
    if os.path.exists(path):
        return f"[ERROR] Group '{name}' already exists"
    os.makedirs(path)
    os.makedirs(os.path.join(path, "queue"), exist_ok=True)

    # meta.json
    meta = {
        "group_id": str(uuid.uuid4()),
        "creator": creator,
        "leader": creator,
        "script_makers": [],
        "members": [creator]
    }
    with open(os.path.join(path, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # members.json
    with open(os.path.join(path, "members.json"), "w") as f:
        json.dump([creator], f, indent=2)

    # chat.log kosong
    open(os.path.join(path, "chat.log"), "w").close()
    return f"[OK] Group '{name}' created by {creator}"

#def grouplist():
 #   groups = [d for d in os.listdir(GROUPS_DIR) if os.path.isdir(os.path.join(GROUPS_DIR, d))]
  #  return groups

def groupsettings(name):
    path = group_path(name)
    meta_file = os.path.join(path, "meta.json")
    if not os.path.exists(meta_file):
        return None
    with open(meta_file) as f:
        return json.load(f)

def grouplist():
    groups = load_groups()
    return list(groups.keys())
