#!/usr/bin/env python3
"""
Automatic Port Liberation Tool
Detects port conflicts and automatically frees them with user confirmation.
"""

import socket
import subprocess
import sys
import platform
import time
from typing import Optional, Tuple

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0
    finally:
        sock.close()

def get_process_on_port(port: int) -> Optional[Tuple[int, str]]:
    """Get PID and process name using the port."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            cmd = f"lsof -i :{port} -n -P | grep LISTEN | awk '{{print $2, $1}}'"
            output = subprocess.check_output(cmd, shell=True, text=True).strip()
            if output:
                parts = output.split()
                return int(parts[0]), parts[1]
        elif system == "Linux":
            cmd = f"lsof -i :{port} -n -P | grep LISTEN | awk '{{print $2, $1}}'"
            output = subprocess.check_output(cmd, shell=True, text=True).strip()
            if output:
                parts = output.split()
                return int(parts[0]), parts[1]
        elif system == "Windows":
            cmd = f"netstat -ano | findstr :{port}"
            output = subprocess.check_output(cmd, shell=True, text=True).strip()
            if output:
                # Extract PID from last column
                pid = output.split()[-1]
                # Get process name
                cmd2 = f'tasklist /FI "PID eq {pid}" /FO LIST'
                proc_output = subprocess.check_output(cmd2, shell=True, text=True)
                if "Image Name:" in proc_output:
                    proc_name = proc_output.split("Image Name:")[1].split("\n")[0].strip()
                    return int(pid), proc_name
    except (subprocess.CalledProcessError, ValueError, IndexError):
        return None
    return None

def kill_process(pid: int, process_name: str) -> bool:
    """Kill a process by PID."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
        else:
            subprocess.run(["kill", "-9", str(pid)], check=True, capture_output=True)
        print(f"✅ Killed {process_name} (PID: {pid})")
        time.sleep(0.5)  # Give OS time to free the port
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to kill process: {e}")
        return False

def find_free_port(start_port: int, max_attempts: int = 50) -> int:
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

def free_port_interactive(port: int) -> bool:
    """Interactively free a port by killing its process."""
    if not is_port_in_use(port):
        return True  # Already free
    
    process_info = get_process_on_port(port)
    if not process_info:
        print(f"⚠️  Port {port} is in use but couldn't identify process")
        return False
    
    pid, process_name = process_info
    print(f"\n🔴 Port {port} is in use by: {process_name} (PID: {pid})")
    
    # Check if it's a Docker container
    if "docker" in process_name.lower() or "com.docker" in process_name.lower():
        print("   This is a Docker container. It will be stopped.")
        response = "y"
    else:
        response = input(f"Kill this process? (y/n): ").lower().strip()
    
    if response == 'y':
        return kill_process(pid, process_name)
    else:
        print(f"❌ Port {port} still in use. Cannot proceed.")
        return False

def free_port_auto(port: int, process_type: str = "service") -> bool:
    """Automatically free a port without prompting (for Docker services)."""
    if not is_port_in_use(port):
        return True  # Already free
    
    process_info = get_process_on_port(port)
    if not process_info:
        print(f"⚠️  Port {port} is in use but couldn't identify process")
        return False
    
    pid, process_name = process_info
    print(f"🔴 Port {port} is in use by: {process_name} (PID: {pid})")
    
    # Auto-kill Docker containers or previous instances
    if any(x in process_name.lower() for x in ["docker", "python", "node", "java", "ollama", "postgres"]):
        print(f"🔨 Auto-killing {process_name}...")
        return kill_process(pid, process_name)
    else:
        print(f"⚠️  Port {port} is used by {process_name}. Requires manual intervention.")
        return False

def check_and_free_ports(ports: dict, auto_mode: bool = False) -> bool:
    """
    Check and free multiple ports.
    
    Args:
        ports: Dict of {port: service_name}
        auto_mode: If True, auto-kill processes. If False, ask user.
    
    Returns:
        True if all ports are free, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"🔍 Checking {len(ports)} ports...")
    print(f"{'='*60}\n")
    
    all_free = True
    for port, service_name in ports.items():
        if is_port_in_use(port):
            all_free = False
            if auto_mode:
                free_port_auto(port, service_name)
            else:
                free_port_interactive(port)
        else:
            print(f"✅ {service_name:25s} (Port {port:5d}) - FREE")
    
    print(f"\n{'='*60}")
    
    # Final check
    time.sleep(1)
    all_still_free = all(not is_port_in_use(port) for port in ports.keys())
    
    if all_still_free:
        print("✅ All ports are now FREE!")
        return True
    else:
        print("❌ Some ports are still in use")
        return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatic Port Liberation Tool")
    parser.add_argument("--auto", action="store_true", help="Auto-kill processes without asking")
    parser.add_argument("--ports", type=str, default="8000,3000,5432,5000", 
                       help="Comma-separated ports to check (default: 8000,3000,5432,5000)")
    args = parser.parse_args()
    
    # Parse ports
    try:
        port_list = [int(p.strip()) for p in args.ports.split(",")]
    except ValueError:
        print("❌ Invalid port list")
        return 1
    
    port_map = {
        8000: "Backend API",
        3000: "Frontend (Vite)",
        5432: "Database (PostgreSQL)",
        5000: "LLM Wrapper (Flask)",
        11434: "Ollama (Host)"
    }
    
    ports_to_check = {p: port_map.get(p, f"Port {p}") for p in port_list}
    
    if check_and_free_ports(ports_to_check, auto_mode=args.auto):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
