# Single Container Docker Setup for ImageGenAI

This document provides instructions for running the ImageGenAI application using a single Docker container that runs both the frontend and backend services.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### Development Mode (Single Container)

To run the application in development mode with hot reloading in a single container:

```bash
# Start development environment in single container
docker-compose -f docker-compose.dev-single.yml up -d --build

# Or use the convenient script
./docker-scripts.sh dev-single
```

### Production Mode (Single Container)

To run the application in production mode in a single container:

```bash
# Start production environment in single container
docker-compose -f docker-compose.single.yml up -d --build

# Or use the convenient script
./docker-scripts.sh prod-single
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Single Container Architecture

### Benefits of Single Container Approach

- **Simplified deployment**: Only one container to manage
- **Reduced resource usage**: Shared base image and dependencies
- **Easier networking**: No need for inter-container communication
- **Simplified orchestration**: Single container to start/stop
- **Cost effective**: Lower resource requirements

### Container Structure

The single container runs both services using a startup script:

1. **Backend Service**: FastAPI application running on port 8000
2. **Frontend Service**: Next.js application running on port 3000
3. **Shared Dependencies**: Both services share the same container environment

## Services

### Backend (FastAPI)
- **Port**: 8000
- **Health Check**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/api/docs
- **Environment**: Development/Production
- **Volumes**: 
  - Development: Full source code mounted for hot reloading
  - Production: Built application with optimized images

### Frontend (Next.js)
- **Port**: 3000
- **Environment**: Development/Production
- **Volumes**: 
  - Development: Full source code mounted for hot reloading
  - Production: Built application with optimized static files

## Environment Variables

### Backend
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: true for dev, false for prod)
- `FRONTEND_URL`: Frontend URL for CORS
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins

### Frontend
- `NODE_ENV`: Node environment (development/production)
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Useful Commands

### View Logs
```bash
# All services in single container
docker-compose -f docker-compose.dev-single.yml logs
docker-compose -f docker-compose.single.yml logs

# Or use the script
./docker-scripts.sh logs
```

### Stop Services
```bash
# Stop single container
docker-compose -f docker-compose.dev-single.yml down
docker-compose -f docker-compose.single.yml down

# Or use the script
./docker-scripts.sh stop
```

### Rebuild Services
```bash
# Rebuild single container
docker-compose -f docker-compose.dev-single.yml build
docker-compose -f docker-compose.single.yml build

# Or use the script
./docker-scripts.sh build
```

### Access Container Shell
```bash
# Access shell in single container
docker-compose -f docker-compose.dev-single.yml exec app bash
docker-compose -f docker-compose.single.yml exec app bash

# Or use the script
./docker-scripts.sh shell
```

## Management Script

The `docker-scripts.sh` script provides convenient commands for single container setup:

```bash
./docker-scripts.sh dev-single   # Start development in single container
./docker-scripts.sh prod-single  # Start production in single container
./docker-scripts.sh stop         # Stop all containers
./docker-scripts.sh logs         # View logs
./docker-scripts.sh shell        # Open shell in container
./docker-scripts.sh status       # Show container status
./docker-scripts.sh clean        # Clean up everything
```

## Development Workflow

1. Make changes to your code
2. In development mode, changes are automatically reflected with hot reloading
3. Both frontend and backend will restart automatically when files change
4. View logs to see both services running in the same container

## Production Deployment

For production deployment with single container:

1. Use `docker-compose.single.yml` or `./docker-scripts.sh prod-single`
2. The container will build the frontend and serve it statically
3. Both services run in the same container with optimized performance
4. Single container makes deployment and scaling simpler

## Troubleshooting

### Port Conflicts
If you get port conflicts:
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000

# Kill processes or change ports in docker-compose files
```

### Container Issues
```bash
# Check container status
docker-compose -f docker-compose.dev-single.yml ps

# View detailed logs
docker-compose -f docker-compose.dev-single.yml logs -f

# Restart container
docker-compose -f docker-compose.dev-single.yml restart
```

### Clean Up
```bash
# Remove single container and volumes
docker-compose -f docker-compose.dev-single.yml down -v
docker-compose -f docker-compose.single.yml down -v

# Or use the script
./docker-scripts.sh clean
```

## Comparison: Multi-container vs Single Container

| Feature | Multi-container | Single Container |
|---------|----------------|------------------|
| **Complexity** | Higher | Lower |
| **Resource Usage** | Higher | Lower |
| **Networking** | Inter-container | Internal |
| **Scaling** | Independent | Together |
| **Debugging** | Separate logs | Combined logs |
| **Deployment** | Multiple containers | Single container |
| **Development** | Hot reload both | Hot reload both |

Choose single container for:
- Simpler deployments
- Lower resource usage
- Easier development setup
- Single service scaling

Choose multi-container for:
- Independent scaling
- Service isolation
- Microservices architecture
- Complex networking requirements
