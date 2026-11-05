import './assets/main.css'
import './assets/vantbottombutton.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useUserStore } from './stores/user.ts'
import Vant from 'vant'

import 'element-plus/dist/index.css'
import 'vant/lib/index.css'
import router from './router'
const app = createApp(App)

app.use(createPinia())

const userStore = useUserStore()
userStore.checkAuth()

app.use(ElementPlus, {
  locale: zhCn,
})
app.use(Vant)
app.use(router)

app.mount('#app')
