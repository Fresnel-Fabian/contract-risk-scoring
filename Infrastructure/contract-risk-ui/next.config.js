/** @type {import('next').NextConfig} */
const nextConfig = {
  // Point this at your Python backend when running locally
  async rewrites() {
    return [
      {
        source: '/api/score',
        destination: process.env.BACKEND_URL
          ? `${process.env.BACKEND_URL}/score`
          : 'http://localhost:8080/analyze',
      },
    ]
  },
}

module.exports = nextConfig
