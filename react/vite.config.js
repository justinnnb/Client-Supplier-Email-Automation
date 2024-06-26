import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  },
  server: {
    proxy: {
      '/api': {
           target: 'http://127.0.0.1:5010',
           changeOrigin: true,
           secure: false,
           rewrite: (path) => path.replace(/^\/api/, ''),
       }
  }
  }

  
})
