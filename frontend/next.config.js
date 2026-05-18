/** @type {import('next').NextConfig} */
const BACKEND_PORT = process.env.BACKEND_PORT || '8055';
const BACKEND_URL = process.env.BACKEND_URL || `http://localhost:${BACKEND_PORT}`;

const nextConfig = {
  reactStrictMode: true,

  // API proxy to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || BACKEND_URL,
    NEXT_PUBLIC_APP_NAME: 'PDF Document Extraction',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },

  // Image optimization
  images: {
    domains: ['localhost'],
  },
};

module.exports = nextConfig;
