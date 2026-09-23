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
    const res = await service.get('/api/check-auth')

    try {
      const data = await res.data
      if (data) {
        loggedIn.value = !!data.logged_in
        userInfo.value = data
      }
      loaded.value = true
    } catch (error) {
      console.error('解析认证响应时出错:', error)
      throw error // 继续抛出错误，以便上层处理
    } finally {
      loaded.value = true
    }
  }

  async function login(user_name: string, password: string) {
    const res = await service.post('/api/login', { user_name, password })
    const data = await res.data
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    await checkAuth()
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
    await checkAuth()
  }
  function logout() {
    localStorage.removeItem('access_token')
    loggedIn.value = false
    userInfo.value = null
    loaded.value = true
  }

  return { loggedIn, userInfo, loaded, checkAuth, login, register, logout }
})
