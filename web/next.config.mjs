/** @type {import('next').NextConfig} */
const nextConfig = {
  // Cloudflare Pages compatibility
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    unoptimized: true, // Required for some free hosting environments
  },
};

export default nextConfig;
