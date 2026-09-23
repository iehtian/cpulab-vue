import axios from 'axios'
import type { AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  timeout: 1000,
})

// 常见 HTTP 状态码对应的错误提示
const httpErrorMessage: Record<number, string> = {
  400: '请求参数错误，请检查输入',
  401: '登录状态已过期，请重新登录',
  403: '没有权限执行此操作',
  404: '请求的资源不存在',
  408: '请求超时，请稍后重试',
  500: '服务器内部错误，请稍后重试',
  502: '网关错误，请稍后重试',
  503: '服务暂不可用，请稍后重试',
  504: '网关超时，请稍后重试',
}

// 添加请求拦截器
service.interceptors.request.use(
  function (config) {
    // 在发送请求之前做些什么
    config.headers['Content-Type'] = 'application/json'
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }

    return config
  },
  function (error) {
    // 对请求错误做些什么
    return Promise.reject(error)
  },
)

// 添加响应拦截器
service.interceptors.response.use(
  function (response) {
    // 2xx 范围内的状态码都会触发该函数。
    // 对响应数据做点什么
    return response
  },
  function (error: AxiosError<{ message?: string; msg?: string }>) {
    // 超出 2xx 范围的状态码都会触发该函数。
    // 请求被主动取消时不提示错误
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    // 优先使用后端返回的错误信息
    const backendMessage = error.response?.data?.message || error.response?.data?.msg

    if (error.response) {
      const { status } = error.response

      // 401：登录态失效，清理本地登录凭证
      if (status === 401) {
        localStorage.removeItem('access_token')
      }

      ElMessage.error(backendMessage || httpErrorMessage[status] || `请求失败（${status}）`)
    } else if (error.code === 'ECONNABORTED' || /timeout/i.test(error.message)) {
      // 请求超时
      ElMessage.error('请求超时，请检查网络后重试')
    } else if (error.code === 'ERR_NETWORK') {
      // 网络断开、跨域或服务器不可达
      ElMessage.error('网络异常，请检查网络连接')
    } else {
      ElMessage.error('请求失败，请稍后重试')
    }

    return Promise.reject(error)
  },
)

export default service
