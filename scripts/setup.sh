#!/bin/bash
# Auto-generate .env files from .env.example templates
# Run this once after cloning the repository

set -e

echo "🔧 Setting up PMBOT environment files..."

# Backend .env
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo "✅ backend/.env created. Update OAuth credentials if needed."
else
    echo "⏭️  backend/.env already exists, skipping."
fi

# Frontend .env
if [ ! -f Frontend/.env ]; then
    echo "📝 Creating Frontend/.env from template..."
    cp Frontend/.env.example Frontend/.env
    echo "✅ Frontend/.env created."
else
    echo "⏭️  Frontend/.env already exists, skipping."
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Ensure Ollama is running on your host machine:"
echo "     - Download: https://ollama.ai"
echo "     - Run: ollama serve"
echo ""
echo "  2. Verify models are downloaded:"
echo "     - ollama pull llama3"
echo "     - ollama pull qwen2:7b-instruct"
echo ""
echo "  3. Start the application:"
echo "     - docker compose up --build"
echo ""
echo "  4. Access the application:"
echo "     - Frontend: http://localhost:3000"
echo "     - Backend: http://localhost:8000"
echo ""
echo "💡 For troubleshooting, see SETUP.md"
