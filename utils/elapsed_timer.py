# utils/elapsed_timer.py - Elapsed time tracking

import time

_start_time = None

def start():
    """Start the elapsed time timer."""
    global _start_time
    _start_time = time.time()

def stop():
    """Stop the timer and return elapsed time in seconds."""
    global _start_time
    if _start_time is None:
        return 0
    elapsed = time.time() - _start_time
    _start_time = None
    return elapsed

def reset():
    """Reset the timer."""
    global _start_time
    _start_time = None

def get_elapsed():
    """Get the current elapsed time in seconds without stopping the timer."""
    global _start_time
    if _start_time is None:
        return 0
    return time.time() - _start_time
