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
RUN echo "Building backend..." && cd /app/apps/backend && npm run build || (echo "Backend build failed" && exit 1)
# Install frontend dependencies locally (needed for Next.js to resolve modules)
RUN echo "Installing frontend dependencies..." && cd /app/apps/frontend && npm install --legacy-peer-deps || (echo "Frontend dependency installation failed" && exit 1)
# Build frontend
#
# NOTE: Coolify may inject NODE_ENV=development at build-time, which can cause Next/React to
# use development server rendering internals during `next build` and fail while prerendering.
# Force a production build regardless of external build-time env.
RUN echo "Building frontend..." && cd /app/apps/frontend && NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 npm run build || (echo "Frontend build failed" && exit 1)
#
# Next.js `output: 'standalone'` requires copying static assets and `public/` into the
# standalone directory, otherwise `/_next/static/*` and `/public/*` routes 404 in production.
RUN cd /app/apps/frontend \
    && mkdir -p .next/standalone/.next \
    && cp -R .next/static .next/standalone/.next/static \
    && cp -R public .next/standalone/public

# Create startup script for production
# Frontend uses PORT env var (set by Coolify), defaults to 3000
# Backend runs on fixed internal port 8000
RUN echo '#!/bin/bash\n\
set -e\n\
# Always run the frontend on 3000 *inside the container*.\n\
# Coolify may set PORT (often 8000) for the service, but this container runs\n\
# both backend and frontend; do not let PORT redirect healthchecks or frontend.\n\
FRONTEND_PORT=3000\n\
# Start backend API on port 8000 (internal-only)\n\
# Bind to 127.0.0.1 so it is NOT reachable from outside the container.\n\
cd /app/apps/backend && uvicorn main:app --host 127.0.0.1 --port 8000 &\n\
# Start frontend in production mode on port 3000 (mapped to host via docker)\n\
# next start is incompatible with output: standalone, so run the standalone server.\n\
cd /app/apps/frontend && NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000 node .next/standalone/server.js &\n\
# Wait for both processes\n\
wait\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
# Only expose the frontend port publicly. Backend is internal-only.
EXPOSE 3000

# Health check - check both frontend and backend
# Backend is always 8000, frontend is always 3000 inside the container.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c "curl -f http://127.0.0.1:8000/api/health && curl -f http://127.0.0.1:3000/api/health || exit 1"

# Start both services
CMD ["/app/start.sh"]