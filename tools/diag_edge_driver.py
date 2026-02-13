# tools/diag_edge_driver.py - Diagnostics for Edge browser detection

import logging
import sys
import os
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config
from utils.logger import setup_logging

def find_edge_installations():
    """Find all Edge installations on the system."""
    common_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
    ]
    
    found = []
    for path in common_paths:
        if os.path.exists(path):
            found.append(path)
    
    return found

def run_edge_diagnostics():
    """Run diagnostics for Edge browser detection."""
    setup_logging(log_level='INFO')
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("EDGE BROWSER DIAGNOSTICS")
    logger.info("=" * 60)
    
    # Find Edge installations
    logger.info("\nSearching for Edge installations...")
    edge_paths = find_edge_installations()
    
    if edge_paths:
        logger.info(f"Found {len(edge_paths)} Edge installation(s):")
        for path in edge_paths:
            logger.info(f"  ✓ {path}")
    else:
        logger.warning("No Edge installations found!")
    
    # Check configuration
    try:
        config = Config.from_yaml('config.yaml')
        configured_path = config.browser_path
        logger.info(f"\nConfigured browser path: {configured_path}")
        
        if configured_path and os.path.exists(configured_path):
            logger.info("  ✓ Configured path exists")
        else:
            logger.error("  ✗ Configured path does not exist")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
    
    logger.info("=" * 60)

if __name__ == '__main__':
    run_edge_diagnostics()
