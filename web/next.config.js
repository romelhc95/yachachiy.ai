/** @type {import('next').NextConfig} */
const nextConfig = {
  // Cloudflare Pages compatibility
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
