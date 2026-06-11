// 路由表：4 个页面 —— 首页概览 / 实时监控 / 事件记录 / 系统设置
import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import Dashboard from '../views/Dashboard.vue'
import Monitor from '../views/Monitor.vue'
import Events from '../views/Events.vue'
import Settings from '../views/Settings.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard },
  { path: '/monitor', component: Monitor },
  { path: '/events', component: Events },
  { path: '/settings', component: Settings }
]

export default createRouter({
  history: createWebHashHistory(),
  routes
})
