import os, platform, gzip, requests

DIST = "jammy"
COMPONENT = "main"
UBUNTU_POOL = "https://ports.ubuntu.com"  # WAJIB untuk ARM

def detect_arch():
    a = platform.machine().lower()
    if a in ("aarch64", "arm64"):
        return "arm64"
    if a in ("armv7l", "armhf"):
        return "armhf"
    if a in ("x86_64", "amd64"):
        return "amd64"
    return None

def build_url(arch):
    base = UBUNTU_POOL if arch.startswith("arm") else "https://archive.ubuntu.com/ubuntu"
    return f"{base}/dists/{DIST}/{COMPONENT}/binary-{arch}/Packages.gz"

def is_valid_gzip(path):
    try:
        with gzip.open(path, "rb") as f:
            f.read(10)
        return True
    except:
        return False

def download(url, dest):
    headers = {"User-Agent": "NeoTermOS/1.0"}
    r = requests.get(url, stream=True, headers=headers, allow_redirects=True)
    if r.status_code != 200:
        raise RuntimeError("HTTP error")

    with open(dest, "wb") as f:
        for c in r.iter_content(8192):
            f.write(c)

def boot(api, ROOT):
    repos = os.path.join(ROOT, "repos")
    os.makedirs(repos, exist_ok=True)

    arch = detect_arch()
    if not arch:
        print("[BOOT] Unsupported architecture")
        exit(1)

    repo = os.path.join(repos, f"ubuntu-{arch}-Packages.gz")
    url = build_url(arch)

    print(f"[BOOT] NeoTermOS booting ({arch})")

    if not os.path.exists(repo) or not is_valid_gzip(repo):
        print("[BOOT] Fetching Ubuntu Packages.gz")
        try:
            download(url, repo)
        except Exception as e:
            print("[BOOT] Download failed:", e)
            exit(1)

        if not is_valid_gzip(repo):
            os.remove(repo)
            print("[BOOT] Repo invalid (HTML or error page)")
            exit(1)

        print("[BOOT] Repo ready")
    else:
        print("[BOOT] Repo OK")
