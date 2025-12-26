/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6001/api',
  },
  // Proxy API requests to backend - works in both dev and production
  // This allows frontend to use relative URLs like '/api' which get proxied to backend
  async rewrites() {
    // Use environment variable for backend URL, fallback to 127.0.0.1 for development
    // Using 127.0.0.1 instead of localhost forces IPv4 and avoids IPv6 connection issues
    // In production (Coolify), both services run in the same container, so localhost:8000 works
    // The rewrite happens server-side, so it doesn't trigger browser local network permissions
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:6001'
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
