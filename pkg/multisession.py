import threading

SESSIONS = []

def spawn_session(user, shell_func):
    """
    user: dict info user
    shell_func: function shell(user) dari main.py
    """
    t = threading.Thread(target=shell_func, args=(user,))
    t.start()
    SESSIONS.append(t)
    print(f"[SESSION] Started session for {user['username']}")
