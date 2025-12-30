/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    // Client-side uses relative '/api' (see api.ts). This default is mainly for any SSR/server usage.
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === 'production'
        ? 'http://127.0.0.1:8000/api'
        : 'http://localhost:6001/api'),
  },
  // Disable static optimization - all pages will be rendered dynamically
  output: 'standalone',
  // Proxy API requests to backend - works in both dev and production
  // This allows frontend to use relative URLs like '/api' which get proxied to backend
  async rewrites() {
    // Use environment variable for backend URL, fallback based on env:
    // - production: backend is inside the same container on 127.0.0.1:8000
    // - development: backend runs on 127.0.0.1:6001
    // Using 127.0.0.1 instead of localhost forces IPv4 and avoids IPv6 connection issues
    // In production (Coolify), both services run in the same container, so localhost:8000 works
    // The rewrite happens server-side, so it doesn't trigger browser local network permissions
    const backendUrl =
      process.env.BACKEND_URL ||
      (process.env.NODE_ENV === 'production'
        ? 'http://127.0.0.1:8000'
        : 'http://127.0.0.1:6001')
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
