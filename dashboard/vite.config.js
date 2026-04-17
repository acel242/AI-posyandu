import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    allowedHosts: [
      'localhost',
      '.trycloudflare.com',
      '.loca.lt',
      '.serveo.net',
      '.serveousercontent.com',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})
