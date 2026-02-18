# utils/elapsed_timer.py - Elapsed time tracking

import time

_start_time = None
_paused_elapsed = None

def start():
    """Start the elapsed time timer."""
    global _start_time, _paused_elapsed
    _start_time = time.time()
    _paused_elapsed = None

def stop():
    """Stop the timer and return elapsed time in seconds."""
    global _start_time, _paused_elapsed
    if _start_time is None:
        return 0
    elapsed = time.time() - _start_time
    _start_time = None
    _paused_elapsed = None
    return elapsed

def pause():
    """Pause the timer and save elapsed time without resetting it."""
    global _start_time, _paused_elapsed
    if _start_time is None:
        return _paused_elapsed if _paused_elapsed is not None else 0
    _paused_elapsed = time.time() - _start_time
    _start_time = None
    return _paused_elapsed

def reset():
    """Reset the timer."""
    global _start_time, _paused_elapsed
    _start_time = None
    _paused_elapsed = None

def get_elapsed():
    """Get the current elapsed time in seconds without stopping the timer.
    If paused, returns the paused elapsed time."""
    global _start_time, _paused_elapsed
    if _paused_elapsed is not None:
        return _paused_elapsed
    if _start_time is None:
        return 0
    return time.time() - _start_time
