# tools/diag_combined.py - Combined diagnostics for the application

import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config
from utils.network import is_connected
from utils.logger import setup_logging

def run_diagnostics():
    """Run combined diagnostics to check system status."""
    setup_logging(log_level='INFO')
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("DIAGNOSTIC REPORT - Bing Search Automator (Headless)")
    logger.info("=" * 60)
    
    # Check Python version
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Python Executable: {sys.executable}")
    
    # Check internet connectivity
    logger.info(f"Internet Connectivity: {'✓ Connected' if is_connected() else '✗ Disconnected'}")
    
    # Check configuration
    try:
        config = Config.from_yaml('config.yaml')
        logger.info(f"Configuration loaded successfully from config.yaml")
        logger.info(f"  - Headless Mode: {config.headless}")
        logger.info(f"  - Browser Path: {config.browser_path}")
        logger.info(f"  - Log Level: {config.log_level}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
    
    # Check required modules
    required_modules = ['playwright', 'pyyaml', 'requests']
    logger.info("\nRequired Modules:")
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"  ✓ {module}")
        except ImportError:
            logger.error(f"  ✗ {module} (not installed)")
    
    logger.info("=" * 60)

if __name__ == '__main__':
    run_diagnostics()
