#!/bin/bash

###############################################################################
# ARGO v10 - Full System Startup Script
# Starts both backend and frontend concurrently
###############################################################################

echo "=========================================="
echo "🚀 ARGO v10 Enterprise Platform"
echo "=========================================="
echo ""
echo "Starting full system..."
echo ""

# Make scripts executable
chmod +x start_backend.sh start_frontend.sh

# Function to handle cleanup
cleanup() {
    echo ""
    echo "🛑 Shutting down ARGO v10..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "📡 Starting Backend..."
./start_backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to initialize
sleep 3

# Start frontend in background
echo "🎨 Starting Frontend..."
./start_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ ARGO v10 is running!"
echo "=========================================="
echo ""
echo "📍 Frontend: http://localhost:5000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for background processes
wait
