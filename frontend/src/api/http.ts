// Axios 实例，baseURL 为空 —— 开发环境靠 Vite proxy 转发 /api → 127.0.0.1:8000
import axios from 'axios'

export const http = axios.create({
  baseURL: ''
})
