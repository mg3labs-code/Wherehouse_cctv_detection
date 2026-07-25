import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Listen on LAN so ngrok / phones can reach Vite
    host: true,
    // Allow ngrok / Cloudflare / localtunnel hostnames (Vite 5+ blocks unknown Host by default)
    allowedHosts: true,
    proxy: {
      // One tunnel to :5173 is enough — /api proxies to FastAPI on :8001
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        timeout: 0,
        proxyTimeout: 0,
      },
    },
  },
})
