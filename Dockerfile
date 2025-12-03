# Single Dockerfile for ImageGenAI with Turbo optimization
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

# Install Python dependencies first (better caching)
COPY apps/backend/requirements.txt ./apps/backend/requirements.txt
RUN pip install --no-cache-dir -r apps/backend/requirements.txt

# Copy package files for dependency installation (better layer caching)
COPY package.json package-lock.json turbo.json ./
COPY packages/shared/package.json ./packages/shared/
COPY apps/backend/package.json ./apps/backend/
COPY apps/frontend/package.json ./apps/frontend/

# Install all Node.js dependencies at root level (workspace dependencies)
RUN npm ci --prefer-offline --no-audit

# Copy shared package source files (needed for Turbo build)
COPY packages/shared/ ./packages/shared/

# Copy Python backend code
COPY apps/backend/ ./apps/backend/

# Copy frontend code (node_modules already installed, .dockerignore excludes it)
COPY apps/frontend/ ./apps/frontend/

# Build applications
# Backend build is just a placeholder, frontend needs actual build  
RUN cd /app/apps/backend && npm run build
# Install frontend dependencies locally (needed for Next.js to resolve modules)
RUN cd /app/apps/frontend && npm install --legacy-peer-deps
# Build frontend
RUN cd /app/apps/frontend && npm run build

# Create startup script for production
# Frontend uses PORT env var (set by Coolify), defaults to 3000
# Backend runs on fixed internal port 8000
RUN echo '#!/bin/bash\n\
set -e\n\
# Use PORT env var for frontend (Coolify sets this), default to 3000\n\
# But ensure frontend uses 3000 internally (PORT might be set for host mapping)\n\
FRONTEND_PORT=3000\n\
# Start backend API on port 8000 (internal)\n\
cd /app/apps/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
# Start frontend in production mode on port 3000 (mapped to host via docker)\n\
# Explicitly set PORT to override any env var, use -p flag for Next.js\n\
cd /app/apps/frontend && PORT=3000 npx next start -p 3000 &\n\
# Wait for both processes\n\
wait\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
# Port 3000 is the default main entry point (frontend) - can be overridden by PORT env var
# Port 8000 is for backend API (internal)
EXPOSE 3000 8000

# Health check - check both frontend and backend
# Frontend port uses PORT env var (defaults to 3000), backend is always 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c "curl -f http://localhost:8000/api/health && curl -f http://localhost:${PORT:-3000} || exit 1"

# Start both services
CMD ["/app/start.sh"]