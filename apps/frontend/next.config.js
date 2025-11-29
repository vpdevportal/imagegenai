/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },
  // Proxy API requests to backend - works in both dev and production
  // This allows frontend to use relative URLs like '/api' which get proxied to backend
  async rewrites() {
    // Always proxy /api/* requests to the backend running on port 8000
    // This is especially useful in production when both services are in the same container
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
