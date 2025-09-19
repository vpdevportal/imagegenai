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

# Check if lsof is available
if ! command -v lsof &> /dev/null; then
    print_error "lsof command not found. Please install it:"
    print_error "  macOS: brew install lsof"
    print_error "  Ubuntu/Debian: sudo apt-get install lsof"
    print_error "  CentOS/RHEL: sudo yum install lsof"
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

# Function to kill processes on a port (safer version)
kill_port() {
    local port=$1
    local service_name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port ($service_name) is in use. Attempting to identify and kill only development processes..."
        
        # Get process info for processes using the port
        local pids=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                # Check if it's a development process (python, node, uvicorn, next)
                local cmd=$(ps -p $pid -o comm= 2>/dev/null)
                if [[ "$cmd" =~ (python|node|uvicorn|next|npm) ]]; then
                    print_status "Killing development process $pid ($cmd) on port $port"
                    kill -TERM $pid 2>/dev/null || true
                    sleep 1
                    # If still running, force kill
                    if kill -0 $pid 2>/dev/null; then
                        kill -9 $pid 2>/dev/null || true
                    fi
                else
                    print_warning "Skipping non-development process $pid ($cmd) on port $port"
                fi
            done
        fi
        
        sleep 2
        if check_port $port; then
            print_error "Failed to free port $port. Please manually stop the process using this port."
            print_error "You can check what's using the port with: lsof -i :$port"
            exit 1
        else
            print_success "Successfully freed port $port"
        fi
    else
        print_status "Port $port ($service_name) is available"
    fi
}

# Kill any existing processes on the ports
print_status "Checking and cleaning up ports..."

# Check if Chrome might be using these ports
for port in 8000 3000; do
    chrome_pids=$(lsof -ti :$port 2>/dev/null | xargs -I {} ps -p {} -o comm= 2>/dev/null | grep -i chrome || true)
    if [ -n "$chrome_pids" ]; then
        print_warning "Chrome processes detected on port $port. This might cause Chrome sessions to be cleared."
        print_warning "Consider closing Chrome or using different ports for development."
    fi
done

kill_port 8000 "backend"
kill_port 3000 "frontend"

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
    # Kill background processes (our development servers)
    jobs -p | xargs -r kill 2>/dev/null || true
    
    # Safely kill only development processes on our ports
    for port in 8000 3000; do
        local pids=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                local cmd=$(ps -p $pid -o comm= 2>/dev/null)
                if [[ "$cmd" =~ (python|node|uvicorn|next|npm) ]]; then
                    print_status "Stopping development process $pid ($cmd) on port $port"
                    kill -TERM $pid 2>/dev/null || true
                fi
            done
        fi
    done
    
    print_success "Development servers stopped"
    exit 0
}

# Set up trap to handle Ctrl+C
trap cleanup SIGINT SIGTERM

# Load environment variables from env.dev
if [ -f "env.dev" ]; then
    print_status "Loading environment variables from env.dev..."
    # Create a temporary .env file for the backend with only backend-relevant variables
    cat > apps/backend/.env << EOF
# Backend Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
GOOGLE_AI_API_KEY=$(grep '^GOOGLE_AI_API_KEY=' env.dev | cut -d'=' -f2)
FRONTEND_URL=$(grep '^FRONTEND_URL=' env.dev | cut -d'=' -f2)
ALLOWED_ORIGINS=$(grep '^ALLOWED_ORIGINS=' env.dev | cut -d'=' -f2)
MAX_FILE_SIZE=$(grep '^MAX_FILE_SIZE=' env.dev | cut -d'=' -f2)
ALLOWED_IMAGE_TYPES=$(grep '^ALLOWED_IMAGE_TYPES=' env.dev | cut -d'=' -f2)
EOF
    print_success "Environment variables loaded"
else
    print_warning "env.dev file not found, using system environment variables"
fi

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
