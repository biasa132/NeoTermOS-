# -------------------------
# neo pkg manager apt-style final
# -------------------------
import os, sys, json, gzip, shutil, subprocess, requests, lzma, tarfile, zipfile

COMPONENTS = ["universe", "main", "restricted", "multiverse"]
ROOT = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(ROOT,"bin")
os.environ["PATH"] = f"{BIN}:{os.environ.get('PATH','')}"

class NeoPkg:
    def __init__(self, root):
        self.root = root
        self.repos_dir = os.path.join(root, "repos")
        self.cache = os.path.join(root, "packages", "cache")
        self.bin_dir = os.path.join(root, "bin")
        os.makedirs(self.repos_dir, exist_ok=True)
        os.makedirs(self.cache, exist_ok=True)
        os.makedirs(self.bin_dir, exist_ok=True)

    # -------------------------
    # utils
    # -------------------------
    def _progress(self, done, total):
        if total == 0: return
        pct = int(done*100/total)
        bar = "█"*(pct//2)
        sys.stdout.write(f"\r[{bar:<50}] {pct}%")
        sys.stdout.flush()

    def _download(self, url, dest):
        r = requests.get(url, stream=True, headers={"User-Agent":"NeoTermOS/1.0"}, allow_redirects=True)
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        done = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                if not chunk: continue
                f.write(chunk)
                done += len(chunk)
                self._progress(done, total)
        print()

    def _is_html(self, path):
        with open(path,"rb") as f:
            return f.read(5).lower().startswith(b"<!doc")

    # -------------------------
    # Repo management
    # -------------------------
    def add(self, base_url):
        name = base_url.replace("https://","").replace("/","_")
        meta = {
            "name": name,
            "base": base_url.rstrip("/"),
            "dist": "jammy",
            "arch": "arm64",
            "component": None,
            "packages": None
        }
        path = os.path.join(self.repos_dir, f"{name}.json")
        with open(path,"w") as f: json.dump(meta,f,indent=2)
        print(f"[NEO] Repo added: {name}")

    def update(self):
        print("[NEO] Updating repositories")
        total_pkgs = 0
        for file in os.listdir(self.repos_dir):
            if not file.endswith(".json"): continue
            meta_path = os.path.join(self.repos_dir, file)
            with open(meta_path) as f: meta = json.load(f)
            gz_path = os.path.join(self.repos_dir, f"{meta['name']}.Packages.gz")
            success = False
            for comp in COMPONENTS:
                url = f"{meta['base']}/dists/{meta['dist']}/{comp}/binary-{meta['arch']}/Packages.gz"
                try:
                    print(f"[NEO] Fetching {meta['name']}:{comp}")
                    self._download(url, gz_path)
                    if self._is_html(gz_path): raise Exception("HTML detected")
                    meta["component"] = comp
                    meta["packages"] = gz_path
                    with open(meta_path,"w") as f: json.dump(meta,f,indent=2)
                    total_pkgs += self._count_packages(gz_path)
                    success = True
                    break
                except Exception:
                    continue
            if not success:
                print(f"[NEO] Failed {meta['name']}")
        print(f"[NEO] Update done ({total_pkgs} packages)")

    def _count_packages(self,gz):
        n=0
        with gzip.open(gz,"rt",errors="ignore") as f:
            for line in f:
                if line.startswith("Package:"): n+=1
        return n

    def _iter_packages(self):
        for file in os.listdir(self.repos_dir):
            if not file.endswith(".Packages.gz"): continue
            path = os.path.join(self.repos_dir,file)
            with gzip.open(path,"rt",errors="ignore") as f:
                pkg={}
                for line in f:
                    line=line.strip()
                    if not line:
                        if pkg: yield pkg
                        pkg={}
                        continue
                    if ":" in line:
                        k,v = line.split(":",1)
                        pkg[k.strip()] = v.strip()
                if pkg: yield pkg

    # -------------------------
    # Commands
    # -------------------------
    def list(self):
        pkgs = list(self._iter_packages())
        if not pkgs:
            print("[NEO] No packages available")
            return
        print(f"{'Package':<20} {'Version':<10} {'Size':<10}")
        print("-"*45)
        for p in pkgs:
            name = p.get("Package","N/A")
            ver  = p.get("Version","N/A")
            size = p.get("Size","N/A")
            if size != "N/A":
                try:
                    size = f"{int(size)/1024:.1f} KB"
                except:
                    pass
            print(f"{name:<20} {ver:<10} {size:<10}")
        print(f"\nTotal packages: {len(pkgs)}")

    def search(self, name):
        results = []
        for p in self._iter_packages():
            if name.lower() in p.get("Package","").lower():
                results.append(p)
        if not results:
            print(f"[NEO] No packages found matching '{name}'")
            return
        print(f"=== Search Results for '{name}' ===")
        for pkg in results:
            pkg_name = pkg.get("Package", "N/A")
            version = pkg.get("Version", "N/A")
            desc = pkg.get("Description", "No description")
            size = pkg.get("Size", "N/A")
            if size != "N/A":
                try: size = f"{int(size)/1024:.1f} KB"
                except: pass
            print(f"\nPackage : {pkg_name}\nVersion : {version}\nSize    : {size}\nDesc    : {desc}")
        print(f"\nTotal found: {len(results)}")

    def down(self, *names):
        for name in names:
            found_pkg = None
            suggestions = []
            for p in self._iter_packages():
                if p.get("Package") == name:
                    found_pkg = p
                    break
                if name.lower() in p.get("Package","").lower():
                    suggestions.append(p.get("Package"))

            if not found_pkg:
                print(f"[NEO] Package '{name}' not found in any repo ❌")
                if suggestions:
                    print("[NEO] Did you mean:")
                    for s in suggestions[:5]:
                        print(f"  {s}")
                continue

            filename = found_pkg.get("Filename")
            if not filename:
                print(f"[NEO] No download URL for {name}, skipping")
                continue

            url = f"https://archive.ubuntu.com/ubuntu/{filename}"
            deb = os.path.join(self.cache, os.path.basename(filename))
            try:
                print(f"[NEO] Downloading {name}")
                self._download(url, deb)
                print("[NEO] Installing package")
                self._install_package(deb)
                print(f"[NEO] {name} ready to use ✅")
            except requests.HTTPError as e:
                print(f"[NEO] Failed to download {name}: {e}")

    # -------------------------
    # Installer
    # -------------------------
    def _install_deb(self, deb_path):
        if not shutil.which("dpkg-deb"):
            print("[NEO] dpkg-deb not found! Install Termux dpkg package first.")
            return
        try:
            subprocess.run(["dpkg-deb","-x",deb_path,self.bin_dir], check=True)
            for root_dir, _, files in os.walk(BIN):
                for f in files:
                    os.chmod(os.path.join(root_dir, f), 0o755)
        except Exception as e:
            print("[NEO] Failed to extract:", e)

    def _install_compressed(self, path):
        try:
            fname = os.path.basename(path).replace(".", "_")
            out_path = os.path.join(self.bin_dir, fname)
            with open(path, "rb") as f: content = f.read()
            try: decompressed = lzma.decompress(content)
            except lzma.LZMAError:
                print(f"[NEO] Unknown compression format for {path}, skipping")
                return
            with open(out_path, "wb") as f: f.write(decompressed)
            os.chmod(out_path, 0o755)
            print(f"[NEO] Installed {fname} ✅")
        except Exception as e:
            print("[NEO] Failed to install compressed package:", e)

    def _install_package(self, path):
        ext = path.split(".")[-1]
        if ext == "deb": self._install_deb(path)
        elif ext in ("xz", "lzma"): self._install_compressed(path)
        elif ext == "tar.gz":
            with tarfile.open(path) as tar: tar.extractall(self.bin_dir)
        elif ext == "zip":
            with zipfile.ZipFile(path) as zipf: zipf.extractall(self.bin_dir)
        elif ext == "neo":
            shutil.copy(path, os.path.join(ROOT, "lib"))
        else:
            print("[NEO] Unknown package type, skipping install")
