import { defineStore } from 'pinia'
import { ref } from 'vue'
import service from '@/utils/request'

export const useCheckStore = defineStore('check', () => {
  const loggedIn = ref(false)
  const userInfo = ref(null)
  const loaded = ref(false)

  async function checkAuth() {
    const token = localStorage.getItem('access_token')
    if (!token) return { logged_in: false }
    const controller = new AbortController()
    // 给认证检查稍微更宽松的超时，避免后端轻微抖动导致误报
    const timeoutId = setTimeout(() => {
      controller.abort() // 超时后中止请求
    }, 5000)
    const res = await service.get('/api/check-auth', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      signal: controller.signal,
    })
    // 关键：fetch 已返回，立即清除超时，避免在 res.json() 期间被 abort
    clearTimeout(timeoutId)
    const data = await res.data
    if (data) {
      loggedIn.value = !!data.logged_in
      userInfo.value = data
    }
    loaded.value = true
  }

  async function login(user_name: string, password: string) {
    const res = await service.post('/api/login', { user_name, password })
    const data = await res.data
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    checkAuth()
  }

  // 注册功能
  async function register(user_name: string, email: string, phone: string, password: string) {
    const requestBody = { user_name, email, phone, password }
    console.log('发送的注册请求体:', requestBody) // 调试日志

    const res = await service.post('/api/register', requestBody)
    const data = await res.data
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    checkAuth()
  }
  function logout() {
    localStorage.removeItem('access_token')
    loggedIn.value = false
    userInfo.value = null
    loaded.value = true
  }

  return { loggedIn, userInfo, loaded, checkAuth, login, register, logout }
})
