import sys
import os
import platform
import subprocess
import threading
import time
import re
import json
import urllib.request

# ============================================================
# SETTINGS & CACHE (TODO #3 Bonus)
# ============================================================
MODEL = "qwen2.5:0.5b"
ERROR_CACHE = {}  # Единый кэш

# ============================================================
# COLORS
# ============================================================
class Color:
    RESET = "\033[0m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"

def color_text(text, color):
    return f"{color}{text}{Color.RESET}"

# ============================================================
# TODO #1 & #2: Error Detection & Prompt
# ============================================================
ERROR_PATTERNS = [
    r"Traceback", r"ImportError", r"ModuleNotFoundError", r"SyntaxError", r"TypeError",
    r"command not found", r"No such file", r"Permission denied", r"Segmentation fault",
    r"error:", r"fatal error", r"npm ERR!", r"Connection refused"
]
ERROR_REGEX = re.compile("|".join(ERROR_PATTERNS), re.IGNORECASE)

def build_llm_prompt(error_text):
    return f"Fix this terminal error: {error_text}. Give only 1 sentence fix."

def ask_llm_for_fix(error_text):
    """Прямой запрос к API Ollama — это намного быстрее на Windows."""
    cache_key = re.sub(r'[/\\].*?[/\\ ]', '', error_text)[:100].strip()
    if cache_key in ERROR_CACHE:
        return ERROR_CACHE[cache_key] + " (cached)"

    url = "http://localhost:11434/api/generate"
    data = {
        "model": MODEL,
        "prompt": build_llm_prompt(error_text),
        "stream": False # Ждем полный ответ сразу
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), 
                                   headers={'Content-Type': 'application/json'})
        # Увеличим ожидание до 60 секунд, но через API это должно занять 5-10 сек
        with urllib.request.urlopen(req, timeout=60) as response:
            res = json.loads(response.read().decode('utf-8'))
            suggestion = res.get('response', '').strip()
            ERROR_CACHE[cache_key] = suggestion
            return suggestion
    except Exception as e:
        return f"API Error: {e}"



# ============================================================
# CORE LOGIC: Threaded Capture
# ============================================================
def stream_reader(pipe, is_stderr):
    for line in iter(pipe.readline, ''):
        if not line: break
        
        if is_stderr:
            print(color_text(line.strip(), Color.RED))
            if ERROR_REGEX.search(line):
                print(color_text("  [AI Thinking...]", Color.CYAN))
                fix = ask_llm_for_fix(line)
                print(color_text(f"  💡 FIX: {fix}", Color.CYAN))
        else:
            print(color_text(line.strip(), Color.WHITE))

def run_command(command):
    print(color_text(f"--- Running: {' '.join(command)} ---", Color.BOLD))
    
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        shell=(platform.system() == "Windows")
    )

    t1 = threading.Thread(target=stream_reader, args=(proc.stdout, False))
    t2 = threading.Thread(target=stream_reader, args=(proc.stderr, True))
    
    t1.start()
    t2.start()

    try:
        proc.wait()
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        proc.terminate()
        print("\nStopped.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
    else:
        run_command(sys.argv[1:])