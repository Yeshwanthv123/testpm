#!/usr/bin/env python3
"""
PMBOT Complete Startup Orchestrator
This is the master script that handles:
1. Port liberation
2. Health checks
3. Service startup
4. Status monitoring
"""

import subprocess
import sys
import platform
import time
import socket
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class PMBOTOrchestrator:
    def __init__(self):
        self.system = platform.system()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ports_config = {
            8000: "Backend API",
            3000: "Frontend",
            5432: "Database",
            5000: "LLM Wrapper",
        }
        self.services_status = {}
        
    def log(self, level: str, message: str):
        """Print colored log messages."""
        colors = {
            "INFO": "\033[94m",
            "OK": "\033[92m",
            "ERROR": "\033[91m",
            "WARN": "\033[93m",
            "HEADER": "\033[96m",
        }
        end_color = "\033[0m"
        color = colors.get(level, "")
        symbol = {
            "INFO": "ℹ️",
            "OK": "✅",
            "ERROR": "❌",
            "WARN": "⚠️",
            "HEADER": "🔷",
        }.get(level, "•")
        
        print(f"{color}{symbol} {message}{end_color}")
    
    def log_header(self, title: str):
        """Print a section header."""
        print(f"\n\033[96m{'='*60}\033[0m")
        print(f"\033[96m{title:^60}\033[0m")
        print(f"\033[96m{'='*60}\033[0m\n")
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0
        finally:
            sock.close()
    
    def get_process_on_port(self, port: int) -> Tuple[int, str]:
        """Get PID and process name."""
        try:
            if self.system == "Windows":
                cmd = f"netstat -ano | findstr :{port}"
                output = subprocess.check_output(cmd, shell=True, text=True).strip()
                if output:
                    pid = output.split()[-1]
                    cmd2 = f'tasklist /FI "PID eq {pid}" /FO LIST'
                    proc_output = subprocess.check_output(cmd2, shell=True, text=True)
                    if "Image Name:" in proc_output:
                        proc_name = proc_output.split("Image Name:")[1].split("\n")[0].strip()
                        return int(pid), proc_name
            else:
                cmd = f"lsof -i :{port} -n -P 2>/dev/null | grep LISTEN | awk '{{print $2, $1}}' | head -1"
                output = subprocess.check_output(cmd, shell=True, text=True).strip()
                if output:
                    pid, proc = output.split()
                    return int(pid), proc
        except (subprocess.CalledProcessError, ValueError, IndexError):
            pass
        return None, None
    
    def kill_process(self, pid: int, process_name: str) -> bool:
        """Kill a process."""
        try:
            if self.system == "Windows":
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
            else:
                subprocess.run(["kill", "-9", str(pid)], check=True, capture_output=True)
            self.log("OK", f"Killed {process_name} (PID: {pid})")
            time.sleep(0.5)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def free_ports(self) -> bool:
        """Free up ports that are in use."""
        self.log_header("🔨 Port Liberation")
        
        ports_freed = 0
        ports_in_use = {}
        
        # Detect which ports are in use
        for port, service in self.ports_config.items():
            if self.is_port_in_use(port):
                ports_in_use[port] = service
                self.log("WARN", f"{service:25s} (Port {port}) - IN USE")
            else:
                self.log("OK", f"{service:25s} (Port {port}) - FREE")
        
        # Free up ports in use
        if ports_in_use:
            for port, service in ports_in_use.items():
                pid, process_name = self.get_process_on_port(port)
                if pid:
                    self.log("WARN", f"Attempting to free port {port}...")
                    if self.kill_process(pid, process_name):
                        ports_freed += 1
            
            # Verify ports are free
            time.sleep(1)
            still_in_use = [p for p in ports_in_use.keys() if self.is_port_in_use(p)]
            if still_in_use:
                self.log("ERROR", f"These ports are still in use: {still_in_use}")
                return False
        
        self.log("OK", "All ports are FREE!")
        return True
    
    def check_docker(self) -> bool:
        """Check if Docker is running."""
        self.log_header("🐳 Docker Check")
        try:
            subprocess.run(["docker", "ps"], check=True, capture_output=True, timeout=5)
            self.log("OK", "Docker is running")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.log("ERROR", "Docker is NOT running or not installed")
            self.log("WARN", "Please start Docker Desktop or daemon")
            return False
    
    def check_ollama(self) -> bool:
        """Check if Ollama is running."""
        self.log_header("🤖 Ollama Check")
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:11434", timeout=2)
            self.log("OK", "Ollama is running")
            return True
        except:
            self.log("WARN", "Ollama is NOT running")
            self.log("WARN", "Make sure to run: ollama serve")
            return False
    
    def start_docker(self) -> bool:
        """Start docker-compose."""
        self.log_header("🚀 Starting Services")
        self.log("INFO", "Command: docker-compose up --build")
        print()
        try:
            subprocess.run(["docker-compose", "up", "--build"], check=False)
            return True
        except KeyboardInterrupt:
            self.log("WARN", "Startup interrupted by user")
            return False
        except Exception as e:
            self.log("ERROR", f"Error starting docker-compose: {e}")
            return False
    
    def run(self) -> int:
        """Main orchestration."""
        print(f"\n{'='*60}")
        print(f"🚀 PMBOT Startup Orchestrator")
        print(f"System: {self.system}")
        print(f"Time: {self.timestamp}")
        print(f"{'='*60}\n")
        
        # Step 1: Free ports
        if not self.free_ports():
            self.log("ERROR", "Failed to free ports")
            return 1
        
        # Step 2: Check Docker
        if not self.check_docker():
            self.log("ERROR", "Docker check failed")
            return 1
        
        # Step 3: Check Ollama (optional, but recommended)
        ollama_running = self.check_ollama()
        if not ollama_running:
            response = input("\nContinue without Ollama? (y/n): ").lower().strip()
            if response != 'y':
                return 1
        
        # Step 4: Start services
        return 0 if self.start_docker() else 1

def main():
    orchestrator = PMBOTOrchestrator()
    sys.exit(orchestrator.run())

if __name__ == "__main__":
    main()
