# utils/network.py - Network connectivity checks

import socket
import logging

def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Check if the system has internet connectivity."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False

def wait_for_connection(retry_seconds=5, logger=None):
    """Block until internet connectivity is available."""
    import time
    if logger is None:
        logger = logging.getLogger(__name__)
    
    while not is_connected():
        logger.warning(f"No internet connectivity detected. Retrying in {retry_seconds} seconds...")
        time.sleep(retry_seconds)
    logger.info("Internet connectivity restored.")
