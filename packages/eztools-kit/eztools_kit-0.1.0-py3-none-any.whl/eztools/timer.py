import time

_start = None

def start_timer():
    global _start
    _start = time.time()

def stop_timer():
    if _start is None:
        print("Timer was never started.")
        return
    elapsed = time.time() - _start
    print(f"⏱️ Elapsed time: {elapsed:.2f} seconds")