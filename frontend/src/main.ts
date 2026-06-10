// 应用入口：挂载 Vue + Element Plus + Router + Pinia 到 #app
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import './styles/theme.css'

createApp(App).use(createPinia()).use(router).use(ElementPlus).mount('#app')
