#!/usr/bin/env python3
"""
Universal PMBOT Startup Script
Auto-detects OS and runs appropriate startup with port liberation
Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import platform
import os

def run_command(cmd, shell=False):
    """Run a command and return success status."""
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=shell, check=True)
        else:
            result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    system = platform.system()
    
    print("\n" + "="*60)
    print("🚀 PMBOT Universal Startup")
    print("="*60)
    print(f"Detected OS: {system}\n")
    
    # Change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    if system == "Windows":
        print("Running Windows startup script...")
        # Run PowerShell script
        ps_script = os.path.join(script_dir, "auto_start.ps1")
        cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{ps_script}"'
        return run_command(cmd, shell=True)
    
    elif system == "Darwin":  # macOS
        print("Running macOS startup script...")
        # Make script executable
        bash_script = os.path.join(script_dir, "auto_start.sh")
        os.chmod(bash_script, 0o755)
        # Run bash script
        return run_command(f"bash {bash_script}")
    
    elif system == "Linux":
        print("Running Linux startup script...")
        # Make script executable
        bash_script = os.path.join(script_dir, "auto_start.sh")
        os.chmod(bash_script, 0o755)
        # Run bash script
        return run_command(f"bash {bash_script}")
    
    else:
        print(f"❌ Unsupported OS: {system}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
