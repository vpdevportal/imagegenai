#!/bin/bash

# Deployment script for ImageGenAI
# This script takes down containers, rebuilds them, and brings them back up

set -e

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "ImageGenAI Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-cache     Build without using cache"
    echo "  --prod         Deploy in production mode"
    echo "  --dev          Deploy in development mode (default)"
    echo "  --help, -h     Show this help message"
    echo ""
    echo "This script will:"
    echo "1. Take down existing containers"
    echo "2. Rebuild Docker images"
    echo "3. Start containers again"
    echo ""
}

# Function to deploy
deploy() {
    local build_args="$1"
    local mode="$2"
    
    print_status "Starting deployment process..."
    
    # Check if Docker is running
    check_docker
    
    # Step 1: Take down existing containers
    print_status "Step 1/3: Taking down existing containers..."
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        print_success "Containers stopped successfully"
    else
        print_status "No running containers found"
    fi
    
    # Step 2: Rebuild images
    print_status "Step 2/3: Rebuilding Docker images..."
    if [[ "$build_args" == "--no-cache" ]]; then
        print_status "Building without cache..."
        docker-compose build --no-cache
    else
        docker-compose build
    fi
    print_success "Images rebuilt successfully"
    
    # Step 3: Start containers
    print_status "Step 3/3: Starting containers..."
    docker-compose up -d
    
    # Wait a moment for containers to start
    sleep 3
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Deployment completed successfully!"
        echo ""
        print_status "Application URLs:"
        print_status "Frontend: http://localhost:5001"
        print_status "Backend API: http://localhost:6001"
        print_status "API Docs: http://localhost:6001/api/docs"
        echo ""
        print_status "To view logs, run: docker-compose logs -f"
        print_status "To check status, run: docker-compose ps"
    else
        print_error "Deployment failed! Containers are not running."
        print_status "Check logs with: docker-compose logs"
        exit 1
    fi
}

# Parse command line arguments
build_args=""
mode="dev"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            build_args="--no-cache"
            shift
            ;;
        --prod)
            mode="prod"
            shift
            ;;
        --dev)
            mode="dev"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# Run deployment
deploy "$build_args" "$mode"
