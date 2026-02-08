import threading
import socket

SSH_PORT = 2222
SSH_HOST = "0.0.0.0"

def get_prompt(user):
    sym = "#" if user["role"] == "root" else "$"
    path = "/"  # bisa diganti vfs.pwd() kalau ingin full vfs
    return f"NeoTermOS:({user['username']}){sym}{path}$ "

def handle_ssh_client(conn, addr):
    conn.send(b"Welcome to NeoTermOS SSH (root only)\n")
    conn.send(b"Username: ")
    username = conn.recv(1024).decode().strip()

    conn.send(b"Password: ")
    password = conn.recv(1024).decode().strip()

    user = USERS.get(username)
    if not user or password != user["password"] or user["role"] != "root":
        conn.send(b"Authentication failed. Bye.\n")
        conn.close()
        return

    conn.send(b"\nLogin successful! Type 'exit' to quit.\n\n")

    while True:
        prompt = get_prompt(user)
        conn.send(prompt.encode())
        cmd = conn.recv(4096).decode().strip()
        if not cmd: continue
        if cmd in ("exit","quit"):
            conn.send(b"Bye!\n")
            break
        # Jalankan command menggunakan NeoTermOS shell
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
        except Exception as e:
            output = str(e).encode()
        conn.send(output)
        if not output.endswith(b"\n"):
            conn.send(b"\n")
    conn.close()

def start_ssh_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SSH_HOST, SSH_PORT))
    s.listen(5)
    print(f"[SSH] NeoTermOS SSH server running on {SSH_HOST}:{SSH_PORT} (root only)")

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_ssh_client, args=(conn, addr), daemon=True)
        t.start()

# Jalankan SSH server di thread
if IS_ROOT and SSH_MODE:
    threading.Thread(target=start_ssh_server, daemon=True).start()
