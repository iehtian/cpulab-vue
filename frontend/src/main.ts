import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useCheckStore } from './stores/user.ts'

import 'element-plus/dist/index.css'
import router from './router'
const app = createApp(App)

app.use(createPinia())

const checkStore = useCheckStore()
checkStore.checkAuth()

app.use(ElementPlus, {
  locale: zhCn,
})
app.use(router)

app.mount('#app')
