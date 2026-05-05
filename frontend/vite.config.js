import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: './templates',
  base: '/',  // ✅ CHANGE THIS to '/'
  envDir: '../',
  publicDir: '../static',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    open: true,
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Your backend server
        changeOrigin: true,
      },
      '/superadmin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});