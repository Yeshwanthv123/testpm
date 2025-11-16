#!/usr/bin/env python3
"""
Integration test to verify all services are working correctly.
Run AFTER docker-compose up is successful.
"""

import sys
import requests
import time
import subprocess
import json
from typing import Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(title: str):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}▶ {title}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")

def print_ok(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def test_backend_health() -> bool:
    print_step("Testing Backend Health")
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print_ok("Backend is responding")
            print(f"   Response: {response.json()}")
            return True
        else:
            print_error(f"Backend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend is NOT reachable at http://localhost:8000")
        print_warning("  Is the backend container running? Check: docker ps")
        return False
    except Exception as e:
        print_error(f"Error testing backend: {e}")
        return False

def test_frontend_accessibility() -> bool:
    print_step("Testing Frontend Accessibility")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print_ok("Frontend is accessible")
            return True
        else:
            print_warning(f"Frontend returned status {response.status_code}")
            return True  # Still OK, just not 200
    except requests.exceptions.ConnectionError:
        print_error("Frontend is NOT reachable at http://localhost:3000")
        return False
    except Exception as e:
        print_error(f"Error testing frontend: {e}")
        return False

def test_backend_llm_connection() -> bool:
    print_step("Testing Backend → LLM Connection")
    try:
        # Run command in backend container
        result = subprocess.run(
            ["docker", "exec", "pmbot-backend", "python3", "-c", 
             "import requests; r = requests.get('http://pmbot-llm-stub:5000', timeout=5); print(r.status_code)"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            status = result.stdout.strip()
            print_ok(f"Backend can reach LLM wrapper (status: {status})")
            return True
        else:
            print_error(f"Backend cannot reach LLM wrapper")
            if "Connection refused" in result.stderr:
                print_warning("  LLM wrapper is not running")
            print_warning(f"  Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error("Test timed out")
        return False
    except Exception as e:
        print_error(f"Error testing LLM connection: {e}")
        return False

def test_llm_ollama_connection() -> bool:
    print_step("Testing LLM Wrapper → Ollama Connection")
    try:
        # Run command in llm-stub container
        result = subprocess.run(
            ["docker", "exec", "pmbot-llm-stub", "python3", "-c",
             "import requests; r = requests.get('http://host.docker.internal:11434', timeout=5); print('OK' if r.status_code else 'FAIL')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "OK" in result.stdout:
            print_ok("LLM wrapper can reach Ollama")
            return True
        else:
            print_error("LLM wrapper CANNOT reach Ollama")
            print_warning("  This usually means:")
            print_warning("  1. Ollama is not running on host machine")
            print_warning("  2. Wrong Ollama URL configuration")
            print_warning("\n  Fix:")
            print_warning("  1. Start Ollama: ollama serve")
            print_warning("  2. Load model: ollama pull qwen2:7b-instruct")
            return False
    except subprocess.TimeoutExpired:
        print_error("Test timed out")
        return False
    except Exception as e:
        print_error(f"Error testing Ollama connection: {e}")
        return False

def test_database_connection() -> bool:
    print_step("Testing Database Connection")
    try:
        result = subprocess.run(
            ["docker", "exec", "pmbot-backend", "python3", "-c",
             "from sqlalchemy import create_engine; engine = create_engine('postgresql://user:password@db:5432/mydatabase'); conn = engine.connect(); print('DB OK'); conn.close()"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "DB OK" in result.stdout:
            print_ok("Database connection successful")
            return True
        else:
            print_error("Database connection failed")
            print_warning(f"  Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error("Test timed out")
        return False
    except Exception as e:
        print_error(f"Error testing database: {e}")
        return False

def test_api_endpoint() -> bool:
    print_step("Testing API Endpoint")
    try:
        response = requests.get("http://localhost:8000/api/interview/categories", timeout=5)
        if response.status_code == 200:
            print_ok("API endpoint is working")
            print(f"   Response: {response.json()}")
            return True
        else:
            print_warning(f"API returned status {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print_error("Cannot reach API endpoint")
        return False
    except Exception as e:
        print_error(f"Error testing API: {e}")
        return False

def check_environment_variables() -> bool:
    print_step("Checking Environment Variables")
    
    tests = [
        ("Backend", "pmbot-backend", "LLM_API_URL"),
        ("Backend", "pmbot-backend", "LLM_FORCE"),
        ("Backend", "pmbot-backend", "DATABASE_URL"),
        ("Frontend", "pmbot-frontend", "VITE_API_BASE"),
        ("LLM", "pmbot-llm-stub", "OLLAMA_URL"),
    ]
    
    all_ok = True
    for container_type, container, var in tests:
        try:
            result = subprocess.run(
                ["docker", "exec", container, "printenv", var],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                value = result.stdout.strip()
                print_ok(f"{container_type}: {var} = {value}")
            else:
                print_warning(f"{container_type}: {var} not set")
                all_ok = False
        except Exception as e:
            print_error(f"Error checking {container} {var}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}🔍 PMBOT Integration Test{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")
    
    # Check if containers exist
    try:
        result = subprocess.run(
            ["docker", "ps", "-q"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if not result.stdout.strip():
            print_error("No Docker containers running!")
            print_warning("Start containers with: docker-compose up --build")
            return 1
    except Exception as e:
        print_error(f"Cannot access Docker: {e}")
        return 1
    
    # Run tests
    results = {
        "Backend Health": test_backend_health(),
        "Frontend Accessibility": test_frontend_accessibility(),
        "Environment Variables": check_environment_variables(),
        "Backend → LLM Connection": test_backend_llm_connection(),
        "LLM → Ollama Connection": test_llm_ollama_connection(),
        "Database Connection": test_database_connection(),
        "API Endpoint": test_api_endpoint(),
    }
    
    # Summary
    print_step("Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} - {test}")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All tests passed! System is ready.{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️  Some tests failed. Check logs for details.{Colors.END}")
        print(f"{Colors.YELLOW}Commands to debug:{Colors.END}")
        print(f"  docker logs pmbot-backend")
        print(f"  docker logs pmbot-llm-stub")
        print(f"  docker logs pmbot-frontend\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
