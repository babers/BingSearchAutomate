# tools/run_ensure.py - Ensure dependencies are installed before running

import subprocess
import sys
import os

def run_ensure():
    """Install requirements and run the main application."""
    requirements_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
    
    # Install requirements
    print(f"Installing requirements from {requirements_file}...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
    
    # Run main application
    main_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
    print(f"Running main application: {main_file}")
    subprocess.call([sys.executable, main_file])

if __name__ == '__main__':
    run_ensure()
