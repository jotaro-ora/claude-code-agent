#!/usr/bin/env python3
"""
Simple Crypto Price Monitor Runner

This script runs the simplified crypto price monitor from the project root directory.
It uses periodic polling instead of WebSocket connections for better reliability.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point for the simple crypto price monitor."""
    
    # Get the project structure
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    venv_path = current_dir / 'venv'
    monitor_script = current_dir / 'src' / 'simple_monitor.py'
    
    # Check if virtual environment exists
    if venv_path.exists():
        # Use virtual environment python
        if os.name == 'nt':  # Windows
            python_exe = venv_path / 'Scripts' / 'python.exe'
        else:  # Unix/Linux/macOS
            python_exe = venv_path / 'bin' / 'python'
        
        if not python_exe.exists():
            print("Virtual environment found but Python executable is missing.")
            print(f"Please reinstall dependencies: cd {current_dir} && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
            return 1
            
        print(f"Using virtual environment: {python_exe}")
    else:
        print("Virtual environment not found. Creating and installing dependencies...")
        try:
            # Create virtual environment
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
            
            # Activate and install dependencies
            if os.name == 'nt':
                python_exe = venv_path / 'Scripts' / 'python.exe'
                pip_exe = venv_path / 'Scripts' / 'pip.exe'
            else:
                python_exe = venv_path / 'bin' / 'python'
                pip_exe = venv_path / 'bin' / 'pip'
            
            # Install requirements
            requirements_file = current_dir / 'requirements.txt'
            subprocess.run([str(pip_exe), 'install', '-r', str(requirements_file)], check=True)
            
            print("Virtual environment created and dependencies installed.")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to set up virtual environment: {e}")
            return 1
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Run the monitor script with all command-line arguments
    cmd = [str(python_exe), str(monitor_script)] + sys.argv[1:]
    
    try:
        print(f"Starting simple crypto price monitor from {project_root}")
        print(f"Command: {' '.join(str(c) for c in cmd)}")
        print("Note: This version uses periodic polling instead of WebSocket for better reliability.")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Monitor execution failed: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\nMonitor stopped by user.")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())