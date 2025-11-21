#!/bin/bash

###############################################################################
# ARGO v10 - Backend Startup Script
# Starts FastAPI backend server
###############################################################################

echo "=========================================="
echo "🚀 ARGO v10 Backend Starting..."
echo "=========================================="

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your OpenAI API key"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p data logs temp

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "=========================================="
echo "🌐 Starting FastAPI server on port 8000"
echo "=========================================="
echo ""

# Start the backend
python main.py
