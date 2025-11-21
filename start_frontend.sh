#!/bin/bash

###############################################################################
# ARGO v10 - Frontend Startup Script
# Starts React + Vite frontend
###############################################################################

echo "=========================================="
echo "🚀 ARGO v10 Frontend Starting..."
echo "=========================================="

# Navigate to frontend directory
cd "$(dirname "$0")/frontend_ui"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "=========================================="
echo "🌐 Starting Vite dev server on port 5000"
echo "=========================================="
echo ""

# Start the frontend
npm run dev:client
