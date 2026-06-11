// Axios 实例
// 开发环境：baseURL 为空，靠 Vite proxy 转发 /api → 127.0.0.1:8000
// 生产环境（GitHub Pages）：API 调用会 404，需部署后端后将 baseURL 改为实际后端地址
//   例如: baseURL: 'https://your-server.com'
import axios from 'axios'

export const http = axios.create({
  baseURL: ''
})
