import subprocess
import os

class NeoInterpreter:
    """
    Interpreter sederhana untuk NeoTermOS .neo scripts
    Menjalankan setiap baris script sebagai command shell
    """

    def __init__(self, script_path):
        self.script_path = script_path
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"{script_path} not found")

    def run(self):
        print(f"[NEO INTERPRETER] Running {self.script_path}...\n")
        with open(self.script_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    subprocess.run(line, shell=True, env=os.environ)
                except Exception as e:
                    print(f"[ERROR] executing line: {line}\n{e}")
