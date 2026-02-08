import hashlib
import os

def sha256_file(file_path):
    """Hitung SHA256 dari file apapun"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_file(file_path, expected_sha256):
    """Verifikasi satu file dengan checksum"""
    if not os.path.exists(file_path):
        print(f"[VERIFY] File {file_path} not found ❌")
        return False

    actual_hash = sha256_file(file_path)
    if actual_hash.lower() == expected_sha256.lower():
        print(f"[VERIFY] {os.path.basename(file_path)} verified ✅")
        return True
    else:
        print(f"[VERIFY] {os.path.basename(file_path)} verification FAILED ❌")
        print(f"Expected: {expected_sha256}")
        print(f"Actual  : {actual_hash}")
        return False

def verify_folder(folder_path, checksums):
    """
    Verifikasi semua file di folder.
    - folder_path: folder yang mau dicek
    - checksums: dict, key=filename, value=sha256
    """
    if not os.path.exists(folder_path):
        print(f"[VERIFY] Folder {folder_path} not found ❌")
        return

    for file_name, expected_hash in checksums.items():
        file_path = os.path.join(folder_path, file_name)
        verify_file(file_path, expected_hash)

def verify_all_cache(cache_dir):
    import os
    for root, dirs, files in os.walk(cache_dir):
        for f in files:
            file_path = os.path.join(root, f)
            if os.path.isdir(file_path):  # <-- skip folder otomatis
                continue
            actual_hash = sha256_file(file_path)
            print(f"[VERIFY] {f} SHA256: {actual_hash}")
