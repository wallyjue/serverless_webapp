import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  },
  define: {
    global: 'globalThis',
  },
  build: {
    // 增加 chunk 大小警告限制
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        // 手動分割 chunks 以優化載入性能
        manualChunks: {
          // React 相關
          'react-vendor': ['react', 'react-dom'],
          // Material-UI 相關
          'mui-vendor': [
            '@mui/material', 
            '@mui/icons-material',
            '@emotion/react',
            '@emotion/styled'
          ],
          // AWS 和認證相關
          'aws-vendor': [
            '@aws-amplify/ui-react',
            'aws-amplify'
          ],
          // 路由和 HTTP 客戶端
          'utils-vendor': [
            'react-router-dom',
            'axios'
          ]
        }
      }
    }
  }
})