#!/bin/bash

# ImageGenAI Development Startup Script
# This script starts both the FastAPI backend and Next.js frontend for development

set -e  # Exit on any error

echo "🚀 Starting ImageGenAI Development Environment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "turbo.json" ]; then
    print_error "Please run this script from the root directory of the ImageGenAI project"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are already in use
print_status "Checking if ports are available..."

if check_port 8000; then
    print_warning "Port 8000 (backend) is already in use. Backend might already be running."
fi

if check_port 3000; then
    print_warning "Port 3000 (frontend) is already in use. Frontend might already be running."
fi

# Check if Python virtual environment exists
if [ ! -d "apps/backend/venv" ]; then
    print_status "Creating Python virtual environment..."
    cd apps/backend
    python3 -m venv venv
    cd ../..
    print_success "Python virtual environment created"
fi

# Check if backend dependencies are installed
if [ ! -d "apps/backend/venv/lib/python3.*/site-packages/fastapi" ]; then
    print_status "Installing backend dependencies..."
    cd apps/backend
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../..
    print_success "Backend dependencies installed"
fi

# Check if frontend dependencies are installed
if [ ! -d "apps/frontend/node_modules" ]; then
    print_status "Installing frontend dependencies..."
    cd apps/frontend
    npm install
    cd ../..
    print_success "Frontend dependencies installed"
fi

print_status "Starting development servers..."
echo ""

# Create a function to handle cleanup on exit
cleanup() {
    print_status "Shutting down development servers..."
    # Kill background processes
    jobs -p | xargs -r kill
    exit 0
}

# Set up trap to handle Ctrl+C
trap cleanup SIGINT SIGTERM

# Start backend in background
print_status "Starting FastAPI backend on http://localhost:8000"
cd apps/backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ../..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
print_status "Starting Next.js frontend on http://localhost:3000"
cd apps/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

# Wait a moment for frontend to start
sleep 3

echo ""
print_success "Development environment started successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo ""
echo "📝 Useful Commands:"
echo "   - Press Ctrl+C to stop all servers"
echo "   - Backend logs: Check the terminal output"
echo "   - Frontend logs: Check the terminal output"
echo ""
echo "🔧 Development Tips:"
echo "   - Backend auto-reloads on file changes"
echo "   - Frontend hot-reloads on file changes"
echo "   - API documentation available at /api/docs"
echo ""

# Wait for user to press Ctrl+C
print_status "Press Ctrl+C to stop all servers..."
wait
