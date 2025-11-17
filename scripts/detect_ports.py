#!/usr/bin/env python3
"""
Auto-detect available ports and update configuration files.
Runs before Docker Compose to ensure all ports are available and .env files are updated.
Enhanced with better error handling and edge case management.
"""

import os
import socket
import sys
import json
from pathlib import Path
from typing import Dict, Tuple, Optional

# Port range boundaries (must be > 1024 for non-root users)
MIN_PORT = 1024
MAX_PORT = 65535

def validate_port_range(port: int) -> bool:
    """Validate port is in valid range."""
    return MIN_PORT <= port <= MAX_PORT

def find_available_port(preferred_port: int, start: int = None, end: int = None) -> int:
    """
    Find an available port. If preferred_port is available, return it.
    Otherwise, find the next available port in the range.
    """
    # Validate preferred port
    if not validate_port_range(preferred_port):
        print(f"⚠️  Port {preferred_port} outside valid range ({MIN_PORT}-{MAX_PORT}). Using default.")
        preferred_port = 8000
    
    if start is None:
        start = max(MIN_PORT, preferred_port - 100)
    if end is None:
        end = min(MAX_PORT, preferred_port + 100)
    
    # Ensure start/end are valid
    start = max(MIN_PORT, start)
    end = min(MAX_PORT, end)
    
    # Try the preferred port first
    if is_port_available(preferred_port):
        return preferred_port
    
    # Try ports around the preferred port
    for offset in range(1, 50):
        for port in [preferred_port + offset, preferred_port - offset]:
            if start <= port <= end and is_port_available(port):
                return port
    
    # If nothing found in preferred range, scan from default ports
    for port in range(8000, 9000):
        if is_port_available(port):
            print(f"⚠️  Found available port: {port}")
            return port
    
    # Last resort: let OS find an available port
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    print(f"⚠️  Using OS-assigned port: {port}")
    return port

def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        # Validate port range
        if not validate_port_range(port):
            return False
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except Exception as e:
        print(f"⚠️  Error checking port {port}: {e}")
        return True


def get_current_ports() -> Dict[str, int]:
    """Get current ports from docker-compose.yml with proper error handling."""
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not installed. Installing...\n")
        os.system("pip install pyyaml -q")
        import yaml
    
    docker_compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    
    if not docker_compose_path.exists():
        print(f"⚠️  docker-compose.yml not found at {docker_compose_path}")
        print("    Using default ports...")
        return {}
    
    try:
        with open(docker_compose_path, 'r') as f:
            content = f.read()
            if not content.strip():
                print("⚠️  docker-compose.yml is empty!")
                return {}
            
            config = yaml.safe_load(content)
        
        if config is None:
            print("⚠️  docker-compose.yml is empty or malformed!")
            return {}
        
        ports = {}
        services = config.get('services', {})
        
        if not services:
            print("⚠️  No services found in docker-compose.yml")
            return {}
        
        for service_name, service_config in services.items():
            if service_config is None:
                continue
            
            service_ports = service_config.get('ports', [])
            if service_ports:
                for port_mapping in service_ports:
                    if isinstance(port_mapping, str):
                        try:
                            host_port = int(port_mapping.split(':')[0])
                            if validate_port_range(host_port):
                                ports[service_name] = host_port
                        except (ValueError, IndexError):
                            print(f"⚠️  Invalid port mapping in {service_name}: {port_mapping}")
        
        return ports
    
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in docker-compose.yml: {e}")
        print("    Using default ports...")
        return {}
    except Exception as e:
        print(f"⚠️  Error reading docker-compose.yml: {e}")
        print("    Using default ports...")
        return {}


def detect_and_update_ports() -> Dict[str, Tuple[int, bool]]:
    """
    Detect port changes and update .env files.
    Returns dict of {service: (port, was_changed)}
    """
    
    # Default ports
    default_ports = {
        'pmbot-backend': 8000,
        'pmbot-frontend': 3000,
        'pmbot-db': 5432,
    }
    
    # Get current ports from docker-compose.yml
    current_ports = get_current_ports()
    
    # Detect available ports
    detected_ports = {}
    changes = {}
    
    for service, default_port in default_ports.items():
        current_port = current_ports.get(service, default_port)
        available_port = find_available_port(current_port)
        
        was_changed = available_port != current_port
        detected_ports[service] = available_port
        changes[service] = (available_port, was_changed)
        
        if was_changed:
            print(f"⚠️  {service}: Port {current_port} → {available_port}")
        else:
            print(f"✅ {service}: Port {available_port} available")
    
    # Update .env files
    update_env_files(detected_ports, current_ports)
    
    return changes

def update_env_files(detected_ports: Dict[str, int], current_ports: Dict[str, int]):
    """Update .env files with new ports. Handles missing files and permission errors."""
    
    project_root = Path(__file__).parent.parent
    backend_env = project_root / "backend" / ".env"
    frontend_env = project_root / "Frontend" / ".env"
    
    # Update backend/.env
    if backend_env.exists():
        try:
            with open(backend_env, 'r') as f:
                content = f.read()
            
            backend_port = detected_ports.get('pmbot-backend', 8000)
            db_port = detected_ports.get('pmbot-db', 5432)
            
            # Validate ports
            backend_port = backend_port if validate_port_range(backend_port) else 8000
            db_port = db_port if validate_port_range(db_port) else 5432
            
            lines = content.split('\n')
            new_lines = []
            found_vite = False
            found_db = False
            
            for line in lines:
                if line.startswith('VITE_API_BASE='):
                    new_lines.append(f'VITE_API_BASE=http://localhost:{backend_port}')
                    found_vite = True
                elif line.startswith('DATABASE_URL='):
                    # Extract current DB credentials and update port
                    try:
                        old_url = line.split('=', 1)[1] if '=' in line else ''
                        if 'postgresql://' in old_url:
                            # Parse URL and update port
                            if ':' in old_url:
                                new_url = old_url.rsplit(':', 1)[0] + f':{db_port}'
                            else:
                                new_url = f'{old_url}:{db_port}'
                            new_lines.append(f'DATABASE_URL={new_url}')
                        else:
                            new_lines.append(line)
                    except Exception as e:
                        print(f"⚠️  Error parsing DATABASE_URL: {e}")
                        new_lines.append(line)
                    found_db = True
                else:
                    new_lines.append(line)
            
            # Add missing entries if they don't exist
            if not found_vite:
                new_lines.append(f'VITE_API_BASE=http://localhost:{backend_port}')
            if not found_db:
                new_lines.append(f'DATABASE_URL=postgresql://postgres:password@localhost:{db_port}/pmbot')
            
            with open(backend_env, 'w') as f:
                f.write('\n'.join(new_lines))
            
            print(f"✅ Updated {backend_env}")
        
        except PermissionError:
            print(f"❌ Permission denied updating {backend_env}")
        except Exception as e:
            print(f"⚠️  Could not update {backend_env}: {e}")
    else:
        print(f"⚠️  {backend_env} not found (will be created by Docker)")
    
    # Update Frontend/.env
    if frontend_env.exists():
        try:
            with open(frontend_env, 'r') as f:
                content = f.read()
            
            backend_port = detected_ports.get('pmbot-backend', 8000)
            backend_port = backend_port if validate_port_range(backend_port) else 8000
            
            lines = content.split('\n')
            new_lines = []
            found = False
            
            for line in lines:
                if line.startswith('VITE_API_BASE='):
                    new_lines.append(f'VITE_API_BASE=http://localhost:{backend_port}')
                    found = True
                else:
                    new_lines.append(line)
            
            # Add if missing
            if not found:
                new_lines.append(f'VITE_API_BASE=http://localhost:{backend_port}')
            
            with open(frontend_env, 'w') as f:
                f.write('\n'.join(new_lines))
            
            print(f"✅ Updated {frontend_env}")
        
        except PermissionError:
            print(f"❌ Permission denied updating {frontend_env}")
        except Exception as e:
            print(f"⚠️  Could not update {frontend_env}: {e}")
    else:
        print(f"⚠️  {frontend_env} not found (will be created by Docker)")



def save_port_config(ports: Dict[str, int]):
    """Save port configuration for reference and debugging."""
    config_path = Path(__file__).parent.parent / ".ports.json"
    try:
        # Validate all ports before saving
        validated_ports = {}
        for service, port in ports.items():
            if validate_port_range(port):
                validated_ports[service] = port
            else:
                print(f"⚠️  Skipping invalid port {port} for {service}")
        
        with open(config_path, 'w') as f:
            json.dump(validated_ports, f, indent=2)
        print(f"✅ Saved port configuration to {config_path}")
    except PermissionError:
        print(f"❌ Permission denied saving to {config_path}")
    except Exception as e:
        print(f"⚠️  Could not save port config: {e}")

def detect_and_update_ports() -> Dict[str, Tuple[int, bool]]:
    """
    Detect port changes and update .env files.
    Returns dict of {service: (port, was_changed)}
    """
    
    # Default ports
    default_ports = {
        'pmbot-backend': 8000,
        'pmbot-frontend': 3000,
        'pmbot-db': 5432,
    }
    
    # Get current ports from docker-compose.yml
    current_ports = get_current_ports()
    
    # Detect available ports
    detected_ports = {}
    changes = {}
    
    for service, default_port in default_ports.items():
        current_port = current_ports.get(service, default_port)
        
        # Validate current port
        if not validate_port_range(current_port):
            print(f"⚠️  Invalid port {current_port} for {service}, using default {default_port}")
            current_port = default_port
        
        available_port = find_available_port(current_port)
        
        was_changed = available_port != current_port
        detected_ports[service] = available_port
        changes[service] = (available_port, was_changed)
        
        if was_changed:
            print(f"⚠️  {service}: Port {current_port} → {available_port}")
        else:
            print(f"✅ {service}: Port {available_port} available")
    
    # Update .env files
    update_env_files(detected_ports, current_ports)
    
    # Save configuration
    save_port_config(detected_ports)
    
    return changes

if __name__ == "__main__":
    print("🔍 Detecting and configuring ports...\n")
    
    try:
        changes = detect_and_update_ports()
        
        # Check if any ports changed
        any_changed = any(was_changed for _, (_, was_changed) in changes.items())
        
        if any_changed:
            print("\n⚠️  Port changes detected! .env files have been updated.")
            print("    Docker containers will use the updated ports.")
        else:
            print("\n✅ All ports are available and configured correctly!")
        
        print("\n📝 Port Configuration Summary:")
        for service, (port, changed) in changes.items():
            status = "🔄 CHANGED" if changed else "✅ OK"
            print(f"   {service}: {port} [{status}]")
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n⚠️  Port detection cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
