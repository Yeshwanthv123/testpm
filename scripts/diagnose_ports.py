#!/usr/bin/env python3
"""
Diagnostic script to check port availability and service connectivity.
Run this before starting Docker to identify port conflicts.
"""

import socket
import sys
import subprocess
import platform

def check_port(port):
    """Check if a port is in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def get_process_on_port(port):
    """Get process name using the port."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            cmd = f"lsof -i :{port} | grep LISTEN"
            output = subprocess.check_output(cmd, shell=True, text=True)
            return output.strip()
        elif system == "Linux":
            cmd = f"lsof -i :{port} | grep LISTEN"
            output = subprocess.check_output(cmd, shell=True, text=True)
            return output.strip()
        elif system == "Windows":
            cmd = f"netstat -ano | findstr :{port}"
            output = subprocess.check_output(cmd, shell=True, text=True)
            return output.strip()
    except subprocess.CalledProcessError:
        return None

def check_docker():
    """Check if Docker is running."""
    try:
        subprocess.check_output(["docker", "ps"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("=" * 60)
    print("🔍 PMBOT Port & Service Diagnostic")
    print("=" * 60)
    
    # Check Docker
    print("\n📦 Docker Status:")
    if check_docker():
        print("✅ Docker is running")
    else:
        print("❌ Docker is NOT running or not installed")
        print("   Start Docker Desktop or daemon and retry")
        return 1
    
    # Check ports
    ports = {
        8000: "Backend API",
        3000: "Frontend (Vite)",
        5432: "PostgreSQL",
        5000: "LLM Wrapper",
        11434: "Ollama (host)"
    }
    
    print("\n🔗 Port Status:")
    print("-" * 60)
    all_free = True
    
    for port, service in ports.items():
        in_use = check_port(port)
        status = "❌ IN USE" if in_use else "✅ FREE"
        print(f"  {port:5d} - {service:25s} {status}")
        
        if in_use:
            all_free = False
            process = get_process_on_port(port)
            if process:
                print(f"           Process: {process}")
    
    print("-" * 60)
    
    if all_free:
        print("\n✅ All ports are available! Safe to start Docker.")
        return 0
    else:
        print("\n❌ Some ports are in use. Here's what to do:\n")
        print("   Option 1: Kill conflicting processes")
        print("   Option 2: Change ports in docker-compose.yml")
        print("             Example: '8001:8000' instead of '8000:8000'")
        print("             Then update VITE_API_BASE: http://localhost:8001\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
