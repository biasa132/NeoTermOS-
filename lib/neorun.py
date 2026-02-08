import os
from neo_interpreter import NeoInterpreter

def run_neo(script_path):
    # Jika script tidak ada ekstensi, biarkan
    if not os.path.exists(script_path):
        print(f"[NEO SCRIPT] {script_path} not found ❌")
        return

    try:
        interpreter = NeoInterpreter(script_path)
        interpreter.run()
    except Exception as e:
        print(f"[NEO SCRIPT] Failed to run {script_path}\n{e}")
