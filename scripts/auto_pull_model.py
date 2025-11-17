#!/usr/bin/env python3
"""
Ollama Model Auto-Puller
Ensures the required model is downloaded before starting PMBOT
"""

import subprocess
import sys
import time
import requests
from typing import Optional

def is_ollama_running(url: str = "http://localhost:11434", timeout: int = 5) -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def wait_for_ollama(max_wait: int = 120) -> bool:
    """Wait for Ollama to start, up to max_wait seconds."""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if is_ollama_running():
            print("✅ Ollama is running")
            return True
        print("⏳ Waiting for Ollama to start...")
        time.sleep(3)
    
    print("❌ Ollama did not start in time")
    return False

def get_available_models() -> list:
    """Get list of available models from Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return models
    except:
        pass
    return []

def model_exists(model_name: str) -> bool:
    """Check if a model is already downloaded."""
    models = get_available_models()
    for model in models:
        if model_name in model or model in model_name:
            return True
    return False

def pull_model(model_name: str) -> bool:
    """Pull a model from Ollama."""
    print(f"\n📥 Pulling model: {model_name}")
    print("   This may take 5-15 minutes on first run...")
    print("   Model size: ~4GB\n")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=False,
            text=True,
            timeout=None  # No timeout - model pull can take a while
        )
        
        if result.returncode == 0:
            print(f"\n✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"\n❌ Failed to pull {model_name}")
            return False
    except FileNotFoundError:
        print("❌ Ollama command not found. Is Ollama installed?")
        return False
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def main():
    model_name = "qwen2:7b-instruct"
    
    print("\n" + "="*60)
    print("🤖 Ollama Model Auto-Puller")
    print("="*60)
    print(f"Required model: {model_name}\n")
    
    # Check if Ollama is running
    print("🔍 Checking if Ollama is running...")
    if not wait_for_ollama():
        print("\n❌ Ollama is not running!")
        print("   Please start Ollama with: ollama serve")
        print("   Keep that terminal open while using PMBOT")
        return 1
    
    # Check if model already exists
    print(f"\n🔍 Checking if {model_name} is already downloaded...")
    if model_exists(model_name):
        print(f"✅ Model {model_name} is already available")
        return 0
    
    # Pull the model
    print(f"\n⏳ Model {model_name} not found. Pulling now...")
    if pull_model(model_name):
        print(f"\n✅ Model {model_name} is ready!")
        return 0
    else:
        print(f"\n❌ Failed to pull {model_name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
