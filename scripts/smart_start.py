#!/usr/bin/env python3
"""
Smart startup script that detects port conflicts and suggests alternative ports.
Usage: python scripts/smart_start.py [--port XXXX]
"""

import socket
import subprocess
import json
import sys
import argparse
import platform
from pathlib import Path

def find_free_port(start_port, max_attempts=20):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result != 0:
            return port
    return None

def read_compose():
    """Read docker-compose.yml."""
    try:
        import yaml
        with open('docker-compose.yml', 'r') as f:
            return yaml.safe_load(f)
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description='Smart startup with port conflict detection')
    parser.add_argument('--port', type=int, default=8000, help='Backend port (default: 8000)')
    parser.add_argument('--frontend-port', type=int, default=3000, help='Frontend port (default: 3000)')
    parser.add_argument('--force', action='store_true', help='Force start without checking')
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🚀 PMBOT Smart Startup")
    print("=" * 70)
    
    # Check ports
    backend_free = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('127.0.0.1', args.port)) != 0
    frontend_free = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('127.0.0.1', args.frontend_port)) != 0
    
    if not backend_free:
        print(f"\n⚠️  Port {args.port} is already in use!")
        free_port = find_free_port(args.port + 1)
        if free_port:
            print(f"✅ Found free port: {free_port}")
            print(f"\n📝 To use this port:")
            print(f"   1. Update docker-compose.yml:")
            print(f"      ports:")
            print(f"        - \"{free_port}:8000\"  # changed from {args.port}:8000")
            print(f"\n   2. Update Frontend environment:")
            print(f"      VITE_API_BASE: http://localhost:{free_port}")
            print(f"\n   3. Restart: docker-compose up --build")
            args.port = free_port
        else:
            print(f"❌ Could not find free port")
            return 1
    
    if not frontend_free:
        print(f"\n⚠️  Port {args.frontend_port} is already in use!")
        free_port = find_free_port(args.frontend_port + 1)
        if free_port:
            print(f"✅ Found free port: {free_port}")
            print(f"\n📝 To use this port:")
            print(f"   1. Update docker-compose.yml frontend ports: {free_port}:3000")
            args.frontend_port = free_port
        else:
            print(f"❌ Could not find free port")
            return 1
    
    if backend_free and frontend_free:
        print(f"\n✅ All ports are free!")
        print(f"   Backend:  http://localhost:{args.port}")
        print(f"   Frontend: http://localhost:{args.frontend_port}")
    
    # Start Docker
    print(f"\n🐳 Starting Docker containers...")
    print("   Command: docker-compose up --build\n")
    
    try:
        subprocess.run(['docker-compose', 'up', '--build'], check=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping containers...")
        subprocess.run(['docker-compose', 'down'], check=False)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
