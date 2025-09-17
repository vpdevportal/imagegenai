# Multi-stage build for ImageGenAI - Single container with both frontend and backend
FROM node:18-alpine AS frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY apps/frontend/package*.json ./
RUN npm install
COPY apps/frontend/ .
RUN npm run build

# Final stage with both services
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NODE_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for serving the frontend
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Python dependencies
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY apps/backend/ ./backend/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
COPY --from=frontend-builder /app/frontend/next.config.js ./frontend/
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules

# Create directories
RUN mkdir -p backend/generated_images

# Create startup script
RUN echo '#!/bin/bash\n\
# Start backend in background\n\
cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Start frontend\n\
cd /app/frontend && npm start &\n\
\n\
# Wait for both processes\n\
wait\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health && curl -f http://localhost:3000 || exit 1

# Start both services
CMD ["/app/start.sh"]
