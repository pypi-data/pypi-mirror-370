from datetime import datetime

def log(msg):
    print(f"[{datetime.now().isoformat()}] {msg}")

def log_error(msg):
    print(f"[{datetime.now().isoformat()}] ❌ ERROR: {msg}")