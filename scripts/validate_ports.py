#!/usr/bin/env python3
"""
Validate port configuration in docker-compose.yml and .env files.
Ensures all ports are in valid range and properly configured.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple

def validate_docker_compose():
    """Validate docker-compose.yml port mappings."""
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not installed. Installing...\n")
        os.system("pip install pyyaml -q")
        import yaml
    
    print("📋 Validating docker-compose.yml...\n")
    
    docker_compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    
    if not docker_compose_path.exists():
        print(f"❌ docker-compose.yml not found at {docker_compose_path}")
        return False
    
    try:
        with open(docker_compose_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            print("❌ docker-compose.yml is empty!")
            return False
        
        errors = []
        warnings = []
        services = config.get('services', {})
        
        if not services:
            print("❌ No services found in docker-compose.yml")
            return False
        
        print(f"✅ Found {len(services)} services\n")
        
        for service_name, service_config in services.items():
            print(f"   Service: {service_name}")
            
            if service_config is None:
                warnings.append(f"  ⚠️  {service_name} has no configuration")
                continue
            
            ports = service_config.get('ports', [])
            if ports:
                for port_mapping in ports:
                    if isinstance(port_mapping, str):
                        try:
                            parts = port_mapping.split(':')
                            if len(parts) >= 2:
                                host_port = int(parts[0])
                                container_port = int(parts[1])
                                
                                # Validate ranges
                                if host_port < 1024 or host_port > 65535:
                                    errors.append(f"   ❌ {service_name}: Host port {host_port} out of valid range (1024-65535)")
                                elif container_port < 1 or container_port > 65535:
                                    errors.append(f"   ❌ {service_name}: Container port {container_port} out of valid range")
                                else:
                                    print(f"      ✅ {host_port}:{container_port}")
                            else:
                                errors.append(f"   ❌ {service_name}: Invalid port format '{port_mapping}'")
                        except ValueError as e:
                            errors.append(f"   ❌ {service_name}: Invalid port value in '{port_mapping}': {e}")
                    else:
                        print(f"      ℹ️  Complex port mapping (not string): {port_mapping}")
            else:
                warnings.append(f"   ⚠️  {service_name} has no ports defined")
        
        # Print summary
        print("\n" + "="*60)
        if errors:
            print("\n❌ ERRORS FOUND:")
            for error in errors:
                print(error)
            return False
        else:
            print("\n✅ All port configurations are valid!")
            if warnings:
                print("\n⚠️  Warnings:")
                for warning in warnings:
                    print(warning)
            return True
    
    except Exception as e:
        print(f"❌ Error validating docker-compose.yml: {e}")
        return False

def validate_env_files():
    """Validate .env files have proper API base URLs."""
    print("\n\n📋 Validating .env files...\n")
    
    project_root = Path(__file__).parent.parent
    backend_env = project_root / "backend" / ".env"
    frontend_env = project_root / "Frontend" / ".env"
    
    all_valid = True
    
    # Check backend/.env
    if backend_env.exists():
        print(f"   Checking {backend_env.relative_to(project_root)}...")
        try:
            with open(backend_env, 'r') as f:
                content = f.read()
            
            has_vite_api = 'VITE_API_BASE=' in content
            has_db_url = 'DATABASE_URL=' in content
            has_llm_url = 'LLM_API_URL=' in content
            
            if has_vite_api:
                print("      ✅ VITE_API_BASE found")
            else:
                print("      ⚠️  VITE_API_BASE not found")
            
            if has_db_url:
                print("      ✅ DATABASE_URL found")
            else:
                print("      ⚠️  DATABASE_URL not found")
            
            if has_llm_url:
                print("      ✅ LLM_API_URL found")
            else:
                print("      ⚠️  LLM_API_URL not found (may use default)")
        
        except Exception as e:
            print(f"      ❌ Error reading file: {e}")
            all_valid = False
    else:
        print(f"   ⚠️  {backend_env.relative_to(project_root)} not found")
    
    # Check Frontend/.env
    if frontend_env.exists():
        print(f"\n   Checking {frontend_env.relative_to(project_root)}...")
        try:
            with open(frontend_env, 'r') as f:
                content = f.read()
            
            has_vite_api = 'VITE_API_BASE=' in content
            
            if has_vite_api:
                print("      ✅ VITE_API_BASE found")
            else:
                print("      ⚠️  VITE_API_BASE not found")
        
        except Exception as e:
            print(f"      ❌ Error reading file: {e}")
            all_valid = False
    else:
        print(f"   ⚠️  {frontend_env.relative_to(project_root)} not found")
    
    return all_valid

def check_port_config():
    """Check .ports.json for saved configuration."""
    print("\n\n📋 Checking saved port configuration...\n")
    
    config_path = Path(__file__).parent.parent / ".ports.json"
    
    if not config_path.exists():
        print("   ℹ️  .ports.json not yet created (will be created on first run)")
        return True
    
    try:
        with open(config_path, 'r') as f:
            ports = json.load(f)
        
        print(f"   ✅ Found configuration for {len(ports)} services:")
        
        all_valid = True
        for service, port in ports.items():
            if 1024 <= port <= 65535:
                print(f"      ✅ {service}: {port}")
            else:
                print(f"      ❌ {service}: {port} (invalid range)")
                all_valid = False
        
        return all_valid
    
    except Exception as e:
        print(f"   ❌ Error reading .ports.json: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 Port Configuration Validator")
    print("="*60)
    
    try:
        docker_valid = validate_docker_compose()
        env_valid = validate_env_files()
        ports_valid = check_port_config()
        
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        print(f"Docker Compose: {'✅ VALID' if docker_valid else '❌ INVALID'}")
        print(f"Environment Files: {'✅ VALID' if env_valid else '❌ INVALID'}")
        print(f"Port Config: {'✅ VALID' if ports_valid else '⚠️  NEEDS UPDATE'}")
        
        if docker_valid and env_valid:
            print("\n✅ All validations passed! System is ready.")
            exit(0)
        else:
            print("\n⚠️  Some validations failed. Please review the errors above.")
            exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Validation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
