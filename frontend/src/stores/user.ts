import { defineStore } from 'pinia'
import { ref } from 'vue'
import service from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const loggedIn = ref(false)
  const userName = ref('')
  const userId = ref<number | null>(null)
  const loaded = ref(false)

  async function checkAuth() {
    const token = localStorage.getItem('access_token')
    if (!token) return { logged_in: false }
    const res = await service.get('/api/check-auth')

    try {
      const data = res.data
      console.log('解析认证响应:', data)
      if (data) {
        loggedIn.value = !!data.logged_in
        if (!!data.user_id) userId.value = data.user_id
        if (!!data.user_name) userName.value = data.user_name
      }
    } catch (error) {
      console.error('解析认证响应时出错:', error)
      throw error // 继续抛出错误，以便上层处理
    } finally {
      loaded.value = true
    }
  }

  async function login(username: string, password: string) {
    const res = await service.post('/api/login', { user_name: username, password })
    const data = res.data
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    await checkAuth()
  }

  // 注册功能
  async function register(username: string, email: string, phone: string, password: string) {
    const requestBody = { user_name: username, email, phone, password }
    console.log('发送的注册请求体:', requestBody) // 调试日志

    const res = await service.post('/api/register', requestBody)
    const data = res.data
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    await checkAuth()
  }

  function logout() {
    localStorage.removeItem('access_token')
    loggedIn.value = false
    userName.value = ''
    loaded.value = true
    userId.value = null
  }

  return { loggedIn, userName, loaded, checkAuth, login, register, logout, userId }
})
