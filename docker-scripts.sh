#!/bin/bash

# Docker management scripts for ImageGenAI

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
    echo "ImageGenAI Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev         Start development environment with hot reloading (single container)"
    echo "  prod        Start production environment (single container)"
    echo "  stop        Stop all running containers"
    echo "  restart     Restart all containers"
    echo "  logs        Show logs from all services"
    echo "  logs-backend Show logs from backend only"
    echo "  logs-frontend Show logs from frontend only"
    echo "  build       Build all Docker images"
    echo "  clean       Clean up containers, images, and volumes"
    echo "  status      Show status of all containers"
    echo "  shell       Open shell in container"
    echo "  help        Show this help message"
    echo ""
}

# Function to start development environment (single container)
start_dev() {
    print_status "Starting development environment (single container)..."
    check_docker
    docker-compose up -d --build
    print_success "Development environment started!"
    print_status "Frontend: http://localhost:5001"
    print_status "Backend API: http://localhost:6001"
    print_status "API Docs: http://localhost:6001/api/docs"
}

# Function to start production environment
start_prod() {
    print_status "Starting production environment..."
    check_docker
    docker-compose up -d --build
    print_success "Production environment started!"
    print_status "Frontend: http://localhost:5001"
    print_status "Backend API: http://localhost:6001"
    print_status "API Docs: http://localhost:6001/api/docs"
}

# Function to stop all containers
stop_containers() {
    print_status "Stopping all containers..."
    docker-compose down
    print_success "All containers stopped!"
}

# Function to restart containers
restart_containers() {
    print_status "Restarting containers..."
    stop_containers
    start_dev
}

# Function to show logs
show_logs() {
    print_status "Showing logs from all services..."
    docker-compose logs -f
}

# Function to show backend logs
show_backend_logs() {
    print_status "Showing backend logs..."
    docker-compose logs -f backend
}

# Function to show frontend logs
show_frontend_logs() {
    print_status "Showing frontend logs..."
    docker-compose logs -f frontend
}

# Function to build images
build_images() {
    print_status "Building all Docker images..."
    docker-compose build
    print_success "All images built successfully!"
}

# Function to clean up
clean_up() {
    print_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -a -f
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show status
show_status() {
    print_status "Container status:"
    docker-compose ps
    echo ""
    print_status "Docker system info:"
    docker system df
}

# Function to open shell
open_shell() {
    print_status "Opening shell in container..."
    # Try to find the running container
    if docker-compose ps | grep -q "Up"; then
        docker-compose exec app bash
    else
        print_error "No running containers found"
    fi
}

# Main script logic
case "${1:-help}" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    stop)
        stop_containers
        ;;
    restart)
        restart_containers
        ;;
    logs)
        show_logs
        ;;
    logs-backend)
        show_backend_logs
        ;;
    logs-frontend)
        show_frontend_logs
        ;;
    build)
        build_images
        ;;
    clean)
        clean_up
        ;;
    status)
        show_status
        ;;
    shell)
        open_shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
