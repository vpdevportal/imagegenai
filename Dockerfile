# Single Dockerfile for ImageGenAI
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Python dependencies
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY apps/backend/ ./backend/

# Copy frontend code
COPY apps/frontend/ ./frontend/

# Install frontend dependencies and build for production
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Go back to app root
WORKDIR /app

# Create startup script for production
# Frontend uses PORT env var (set by Coolify), defaults to 3000
# Backend runs on fixed internal port 8000
RUN echo '#!/bin/bash\n\
set -e\n\
# Use PORT env var for frontend (Coolify sets this), default to 3000\n\
FRONTEND_PORT=${PORT:-3000}\n\
# Start backend API on port 8000 (internal)\n\
cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
# Start frontend in production mode using PORT env var\n\
cd /app/frontend && PORT=$FRONTEND_PORT npm run start &\n\
# Wait for both processes\n\
wait\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
# PORT is the main entry point (frontend) - set by Coolify
# Port 8000 is for backend API (internal)
EXPOSE ${PORT:-3000} 8000

# Health check - check both frontend and backend
# Frontend port uses PORT env var, backend is always 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health && curl -f http://localhost:${PORT:-3000} || exit 1

# Start both services
CMD ["/app/start.sh"]