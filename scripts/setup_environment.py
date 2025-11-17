#!/usr/bin/env python3
"""
Smart Environment Setup for PMBOT
Automatically creates .env files from templates if they don't exist
Handles missing environment files gracefully
"""

import os
import sys
import shutil
from pathlib import Path


def get_project_root():
    """Get the project root directory"""
    # This script is in scripts/, so go up one level
    return Path(__file__).parent.parent


def setup_env_file(template_path, target_path, description):
    """
    Copy template to target if target doesn't exist
    
    Args:
        template_path: Path to .env.example
        target_path: Path to .env (destination)
        description: Human-readable description for logging
    """
    template_path = Path(template_path)
    target_path = Path(target_path)
    
    if target_path.exists():
        print(f"✅ {description} already exists: {target_path}")
        return True
    
    if not template_path.exists():
        print(f"⚠️  Template not found: {template_path}")
        # Create a minimal template if it doesn't exist
        create_minimal_template(template_path, description)
        return False
    
    try:
        shutil.copy(template_path, target_path)
        print(f"✅ Created {description}: {target_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to setup {description}: {e}")
        return False


def create_minimal_template(template_path, description):
    """Create minimal .env.example template"""
    template_path = Path(template_path)
    template_path.parent.mkdir(parents=True, exist_ok=True)
    
    if "backend" in str(template_path):
        content = """# Backend environment variables (auto-generated)
JWT_SECRET=dev-secret-change-me
JWT_REFRESH_SECRET=dev-refresh-secret-change-me
SECRET_KEY=a-very-secret-key-that-you-should-change
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
DATABASE_URL=postgresql://user:password@db:5432/mydatabase
FRONTEND_URL=http://localhost:3000
OAUTH_REDIRECT_BASE=http://localhost:8000
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
PM_QUESTIONS_CSV=/backend/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv
OPENAI_API_KEY=
LLM_API_URL=http://pmbot-llm-stub:5000
LLM_MODEL=qwen2:7b-instruct
LLM_FORCE=1
"""
    else:
        content = """# Frontend environment variables (auto-generated)
VITE_API_BASE=http://localhost:8000
REACT_APP_API_BASE=http://localhost:8000
NEXT_PUBLIC_API_BASE=http://localhost:8000
"""
    
    try:
        template_path.write_text(content)
        print(f"📝 Created template: {template_path}")
    except Exception as e:
        print(f"❌ Failed to create template: {e}")


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("🚀 PMBOT Environment Setup")
    print("="*60 + "\n")
    
    root = get_project_root()
    
    # Setup backend .env
    backend_template = root / "backend" / ".env.example"
    backend_env = root / "backend" / ".env"
    setup_env_file(backend_template, backend_env, "Backend .env")
    
    # Setup frontend .env (optional, but good for consistency)
    frontend_template = root / "Frontend" / ".env.example"
    frontend_env = root / "Frontend" / ".env"
    setup_env_file(frontend_template, frontend_env, "Frontend .env")
    
    # Setup root .env (optional)
    root_template = root / ".env.example"
    root_env = root / ".env"
    if root_template.exists():
        setup_env_file(root_template, root_env, "Root .env")
    
    print("\n" + "="*60)
    print("✅ Environment setup complete!")
    print("="*60 + "\n")
    print("Next steps:")
    print("1. Ensure Docker is running")
    print("2. Ensure Ollama is running: ollama serve (in another terminal)")
    print("3. Run: ./run.bat (Windows) or bash run.sh (Mac/Linux)")
    print()


if __name__ == "__main__":
    main()
