#!/bin/bash

echo "========================================"
echo "Starting Sri Lanka Tourism Platform"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo -e "\n${YELLOW}Starting Backend API Server...${NC}"
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo -e "\n${YELLOW}Starting Frontend Development Server...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}========================================"
echo "Platform is running!"
echo "========================================${NC}"
echo ""
echo "Backend API:  http://localhost:5000"
echo "Frontend App: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for processes
wait