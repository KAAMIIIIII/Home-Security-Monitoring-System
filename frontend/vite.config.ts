// Vite 配置：Vue 插件 + 开发代理（/api & /static → 后端 127.0.0.1:8000）
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/Home-Security-Monitoring-System/',
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/static': 'http://127.0.0.1:8000'
    }
  }
})
