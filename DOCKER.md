# Docker Setup for ImageGenAI

This document provides instructions for running the ImageGenAI application using Docker for development.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### Development Mode

To run the application in development mode with hot reloading:

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Or use the convenient script
./docker-scripts.sh dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Services

### Backend (FastAPI)
- **Port**: 8000
- **Health Check**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/api/docs
- **Environment**: Development with hot reloading
- **Volumes**: 
  - Full source code mounted for hot reloading
  - Generated images persisted: `./apps/backend/generated_images:/app/generated_images`

### Frontend (Next.js)
- **Port**: 3000
- **Environment**: Development with hot reloading
- **Volumes**: 
  - Full source code mounted for hot reloading

## Environment Variables

### Backend
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)
- `FRONTEND_URL`: Frontend URL for CORS
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins

### Frontend
- `NODE_ENV`: Node environment (development)
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Useful Commands

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs
docker-compose logs -f
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Or use the script
./docker-scripts.sh stop
```

### Rebuild Services
```bash
# Rebuild specific service
docker-compose build backend

# Rebuild all services
docker-compose build

# Or use the script
./docker-scripts.sh build
```

### Access Container Shell
```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh

# Or use the scripts
./docker-scripts.sh shell-backend
./docker-scripts.sh shell-frontend
```

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Permission Issues
If you encounter permission issues with generated images:
```bash
# Fix ownership
sudo chown -R $USER:$USER ./apps/backend/generated_images
```

### Clean Up
```bash
# Remove all containers, networks, and volumes
docker-compose down -v --remove-orphans

# Remove all images
docker system prune -a

# Or use the script
./docker-scripts.sh clean
```

## Development Workflow

1. Make changes to your code
2. Changes are automatically reflected with hot reloading
3. If you need to rebuild containers:
   ```bash
   docker-compose build backend
   docker-compose up backend
   ```

## Management Script

The `docker-scripts.sh` script provides convenient commands:

```bash
./docker-scripts.sh dev          # Start development environment
./docker-scripts.sh stop         # Stop all containers
./docker-scripts.sh restart      # Restart all containers
./docker-scripts.sh logs         # View logs from all services
./docker-scripts.sh logs-backend # View backend logs only
./docker-scripts.sh logs-frontend # View frontend logs only
./docker-scripts.sh build        # Build all images
./docker-scripts.sh clean        # Clean up everything
./docker-scripts.sh status       # Show container status
./docker-scripts.sh shell-backend # Open backend shell
./docker-scripts.sh shell-frontend # Open frontend shell
```
