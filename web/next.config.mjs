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

export default nextConfig;
