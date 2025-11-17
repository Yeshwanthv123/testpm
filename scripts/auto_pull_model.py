#!/usr/bin/env python3
"""
Ollama Model Auto-Puller
Ensures the required models are downloaded before starting PMBOT
Supports fallback models if primary model is unavailable
"""

import subprocess
import sys
import time
import requests
import os
from typing import Optional, List
from pathlib import Path

# Primary model (optimized for PM questions)
PRIMARY_MODEL = "qwen2:7b-instruct"

# Fallback models if primary is not available
FALLBACK_MODELS = [
    "llama2",
    "neural-chat",
    "mistral",
]

def is_ollama_running(url: str = "http://localhost:11434", timeout: int = 5) -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def wait_for_ollama(max_wait: int = 120, url: str = "http://localhost:11434") -> bool:
    """Wait for Ollama to start, up to max_wait seconds."""
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < max_wait:
        if is_ollama_running(url):
            print("✅ Ollama is running and accessible")
            return True
        
        attempts += 1
        remaining = max_wait - int(time.time() - start_time)
        print(f"⏳ Waiting for Ollama to start... ({remaining}s remaining)")
        time.sleep(3)
    
    print("❌ Ollama did not respond within the timeout period")
    return False

def get_available_models(url: str = "http://localhost:11434") -> List[str]:
    """Get list of available models from Ollama."""
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
            return models
    except Exception as e:
        print(f"⚠️  Error fetching models: {e}")
    return []

def model_exists(model_name: str, url: str = "http://localhost:11434") -> bool:
    """Check if a model is already downloaded."""
    try:
        models = get_available_models(url)
        # Check both full name and base name
        base_model = model_name.split(":")[0]
        return any(base_model in m or m in base_model for m in models)
    except:
        return False

def pull_model(model_name: str, url: str = "http://localhost:11434") -> bool:
    """Pull a model from Ollama."""
    print(f"\n📥 Pulling model: {model_name}")
    print("   This may take 5-15 minutes on first run...")
    print("   Model size: 4-7GB\n")
    
    try:
        # Use ollama API instead of subprocess for better reliability
        pull_url = f"{url}/api/pull"
        
        print(f"   Contacting Ollama at {url}...")
        response = requests.post(
            pull_url,
            json={"name": model_name},
            timeout=1200  # 20 minute timeout
        )
        
        if response.status_code in [200, 201]:
            print(f"\n✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"\n❌ Failed to pull {model_name} (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama. Make sure it's running:")
        print("   ollama serve")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout waiting for model pull. Network issue or very large model.")
        return False
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def validate_model_capability(model_name: str, url: str = "http://localhost:11434") -> bool:
    """Validate that the model can generate text (basic test)."""
    try:
        print(f"\n🧪 Testing model capability...")
        test_url = f"{url}/api/generate"
        
        response = requests.post(
            test_url,
            json={
                "model": model_name,
                "prompt": "What is PM?",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Model {model_name} is working correctly")
            return True
        else:
            print(f"⚠️  Model test returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Could not test model: {e}")
        return True  # Don't fail if test fails

def main():
    """Main function to ensure models are ready."""
    
    print("\n" + "="*60)
    print("🤖 Ollama Model Auto-Setup")
    print("="*60)
    print(f"Primary model: {PRIMARY_MODEL}")
    print(f"Fallback models: {', '.join(FALLBACK_MODELS)}\n")
    
    # Get Ollama URL from environment or use default
    ollama_url = os.environ.get("LLM_API_URL", "http://localhost:11434").rstrip("/")
    
    # Check if Ollama is running
    print("🔍 Checking if Ollama is running...")
    if not wait_for_ollama(url=ollama_url):
        print("\n❌ Ollama is not running!")
        print("\n📋 Setup Instructions:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Start Ollama with: ollama serve")
        print("   3. In another terminal, run this script again\n")
        print("   Or download the model manually:")
        print(f"      ollama pull {PRIMARY_MODEL}")
        return 1
    
    # Check if primary model exists
    print(f"\n🔍 Checking for primary model: {PRIMARY_MODEL}...")
    if model_exists(PRIMARY_MODEL, ollama_url):
        print(f"✅ Model {PRIMARY_MODEL} is already available")
        if validate_model_capability(PRIMARY_MODEL, ollama_url):
            return 0
        else:
            print("⚠️  Model validation failed, proceeding anyway...")
            return 0
    
    # Try to pull primary model
    print(f"\n⏳ Pulling primary model: {PRIMARY_MODEL}...")
    if pull_model(PRIMARY_MODEL, ollama_url):
        if validate_model_capability(PRIMARY_MODEL, ollama_url):
            print(f"\n✅ {PRIMARY_MODEL} is ready!")
            return 0
    
    # Fallback: try alternative models
    print(f"\n⚠️  Primary model pull failed. Trying fallback models...")
    for fallback_model in FALLBACK_MODELS:
        print(f"\n🔄 Checking fallback: {fallback_model}...")
        if model_exists(fallback_model, ollama_url):
            print(f"✅ Found fallback model: {fallback_model}")
            print("   (Performance may be reduced, but PMBOT will work)")
            return 0
        
        print(f"⏳ Pulling fallback model: {fallback_model}...")
        if pull_model(fallback_model, ollama_url):
            print(f"✅ {fallback_model} is ready!")
            print("   (Performance may be reduced, but PMBOT will work)")
            return 0
    
    # If we get here, no models are available
    print("\n❌ No suitable Ollama model found!")
    print("\n📋 Quick Fix:")
    print(f"   Run in a terminal: ollama pull {PRIMARY_MODEL}")
    print(f"   Or try: ollama pull llama2")
    return 1

if __name__ == "__main__":
    sys.exit(main())
