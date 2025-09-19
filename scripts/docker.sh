#!/bin/bash

# ImageGenAI Docker Management Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

show_help() {
    echo "ImageGenAI Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start development environment"
    echo "  stop        Stop all containers"
    echo "  logs        Show logs"
    echo "  build       Build images"
    echo "  clean       Clean up everything"
    echo "  help        Show this help"
    echo ""
}

start_app() {
    print_status "Starting ImageGenAI development environment..."
    docker-compose up --build -d
    print_success "Application started!"
    print_status "Frontend: http://localhost:5001"
    print_status "Backend: http://localhost:6001"
    print_status "API Docs: http://localhost:6001/api/docs"
}

stop_containers() {
    print_status "Stopping containers..."
    docker-compose down
    print_success "Containers stopped!"
}

show_logs() {
    print_status "Showing logs..."
    docker-compose logs -f
}

build_images() {
    print_status "Building images..."
    docker-compose build
    print_success "Images built!"
}

clean_up() {
    print_warning "This will remove all containers, images, and volumes. Continue? (y/N)"
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

case "${1:-help}" in
    start)
        start_app
        ;;
    stop)
        stop_containers
        ;;
    logs)
        show_logs
        ;;
    build)
        build_images
        ;;
    clean)
        clean_up
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
