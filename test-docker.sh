#!/bin/bash

echo "🐳 Testing Docker ImageGenAI Setup"
echo "=================================="

# Check if containers are running
echo "📦 Checking running containers..."
docker ps --filter "name=imagegenai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔍 Testing API endpoints..."

# Test backend health
echo "Testing backend health endpoint..."
curl -f http://localhost:6001/api/health || echo "❌ Backend health check failed"

echo ""
echo "Testing CORS preflight..."
curl -X OPTIONS \
  -H "Origin: http://localhost:5001" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v http://localhost:6001/api/health || echo "❌ CORS preflight failed"

echo ""
echo "🌐 Testing frontend..."
curl -f http://localhost:5001 || echo "❌ Frontend not accessible"

echo ""
echo "📋 Docker logs (last 20 lines)..."
docker logs --tail 20 imagegenai-app-1 2>/dev/null || echo "❌ Could not fetch logs"

echo ""
echo "✅ Test completed!"
