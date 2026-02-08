#!/usr/bin/env python3
import os
import json

class VFS:
    def __init__(self, root, home="/", uid=0, gid=0, is_root=False, perms=None):
        self.root = os.path.abspath(root)
        self.home = os.path.normpath(home)
        self.cwd = self.home
        self.uid = uid
        self.gid = gid
        self.IS_ROOT = is_root

        # Permissions database (dictionary dari main.py)
        self.PERM_DB = perms if perms is not None else {}

    # =========================
    # PATH HELPERS
    # =========================
    def _resolve(self, path):
        if path.startswith("/"):
            abs_path = os.path.normpath(path)
        else:
            abs_path = os.path.normpath(os.path.join(self.cwd, path))
        return abs_path

    def pwd(self):
        return self.cwd

    def cd(self, path):
        vpath = self._resolve(path)
        real = os.path.join(self.root, vpath.strip("/"))
        if not os.path.exists(real):
            print(f"cd: {path}: No such file or directory")
            return
        if not self._check(vpath, "x"):
            print("Permission denied")
            return
        self.cwd = vpath

    def ls(self):
        real = os.path.join(self.root, self.cwd.strip("/"))
        try:
            return os.listdir(real)
        except PermissionError:
            print("Permission denied")
            return []

    # =========================
    # PERMISSIONS
    # =========================
    def _check(self, path, mode):
        # mode = "r", "w", "x"
        if self.IS_ROOT:
            return True
        meta = self.PERM_DB.get(path, {"owner": None, "perm": ""})
        owner = meta.get("owner")
        perms = meta.get("perm", "")
        # Owner has full rights
        if owner == self.uid or owner == self.gid:
            return mode in perms
        return mode in perms

    # =========================
    # CHMOD / CHOWN
    # =========================
    def chmod(self, path, mode, recursive=False):
        if recursive:
            real_path = os.path.join(self.root, path.strip("/"))
            for root_dir, dirs, files in os.walk(real_path):
                rel_root = os.path.relpath(root_dir, self.root)
                self._set_perm(rel_root, mode)
                for f in dirs + files:
                    self._set_perm(os.path.join(rel_root, f), mode)
        else:
            self._set_perm(path, mode)

    def chown(self, path, uid, gid, recursive=False):
        if recursive:
            real_path = os.path.join(self.root, path.strip("/"))
            for root_dir, dirs, files in os.walk(real_path):
                rel_root = os.path.relpath(root_dir, self.root)
                self._set_owner(rel_root, uid, gid)
                for f in dirs + files:
                    self._set_owner(os.path.join(rel_root, f), uid, gid)
        else:
            self._set_owner(path, uid, gid)

    # =========================
    # INTERNAL SETTERS
    # =========================
    def _set_perm(self, path, mode):
        path = self._resolve(path)
        self.PERM_DB[path] = self.PERM_DB.get(path, {})
        self.PERM_DB[path]["perm"] = mode

    def _set_owner(self, path, uid, gid):
        path = self._resolve(path)
        self.PERM_DB[path] = self.PERM_DB.get(path, {})
        self.PERM_DB[path]["owner"] = uid  # bisa juga gid kalau perlu

    # =========================
    # MAKING DIR
    # =========================
    def mkdir(self, path):
        vpath = self._resolve(path)
        real = os.path.join(self.root, vpath.strip("/"))
        os.makedirs(real, exist_ok=True)
        self._set_owner(vpath, self.uid, self.gid)
        self._set_perm(vpath, "rwx")
