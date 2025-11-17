#!/usr/bin/env python3
"""
Smart Port Detection and Allocation
Finds available ports and updates docker-compose.yml dynamically
"""

import socket
import sys
import json
from pathlib import Path


def is_port_available(port):
    """Check if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except Exception:
        return False


def find_available_port(preferred_port, max_attempts=10):
    """
    Find an available port starting from preferred_port
    
    Args:
        preferred_port: Port number to start searching from
        max_attempts: How many ports to try before giving up
    
    Returns:
        Available port number or None
    """
    for offset in range(max_attempts):
        port = preferred_port + offset
        if is_port_available(port):
            return port
    return None


def get_ports():
    """
    Get a mapping of all required ports
    Returns dict with service_name: available_port
    """
    default_ports = {
        'database': 5432,
        'backend': 8000,
        'frontend': 3000,
        'llm_stub': 5000,
    }
    
    available_ports = {}
    
    print("🔍 Scanning for available ports...")
    print()
    
    for service, default_port in default_ports.items():
        available = find_available_port(default_port)
        if available:
            if available == default_port:
                print(f"✅ {service:12} → {available} (default)")
            else:
                print(f"⚠️  {service:12} → {available} (default {default_port} in use, using alternative)")
            available_ports[service] = available
        else:
            print(f"❌ {service:12} → No available port found!")
            return None
    
    print()
    return available_ports


def generate_env_config(ports):
    """Generate environment variable configuration for ports"""
    return {
        'DATABASE_URL': f'postgresql://user:password@db:{ports["database"]}/mydatabase',
        'BACKEND_PORT': str(ports['backend']),
        'FRONTEND_PORT': str(ports['frontend']),
        'LLM_PORT': str(ports['llm_stub']),
        'VITE_API_BASE': f'http://localhost:{ports["backend"]}',
    }


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🔌 PMBOT Smart Port Allocation")
    print("="*60 + "\n")
    
    ports = get_ports()
    
    if not ports:
        print("❌ Could not find available ports")
        return 1
    
    # Generate port summary
    print("="*60)
    print("📋 Port Configuration:")
    print("="*60)
    print(f"Database (PostgreSQL)  → {ports['database']}")
    print(f"Backend (FastAPI)      → {ports['backend']}")
    print(f"Frontend (Vite)        → {ports['frontend']}")
    print(f"LLM Wrapper (Flask)    → {ports['llm_stub']}")
    print()
    print("Access URLs:")
    print(f"  Frontend: http://localhost:{ports['frontend']}")
    print(f"  Backend:  http://localhost:{ports['backend']}")
    print(f"  Docs:     http://localhost:{ports['backend']}/docs")
    print()
    
    # Generate config
    env_config = generate_env_config(ports)
    
    # Output as JSON for docker-compose to use
    print(json.dumps({
        'ports': ports,
        'env': env_config
    }))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
