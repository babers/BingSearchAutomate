# utils/paths.py - Utility for managing app data and resource paths

import os
import sys

def get_app_data_dir():
    """Return the app data directory, creating it if necessary."""
    if sys.platform == 'win32':
        app_data = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
    else:
        app_data = os.path.expanduser('~/.local/share')
    
    app_dir = os.path.join(app_data, 'BingSearchAutomate-Headless')
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def resource_path(relative_path):
    """Return the absolute path to a resource file."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller path
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)
