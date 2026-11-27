// composables/usePermission.ts
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

export function usePermission() {
  const user = useUserStore()

  function has(code?: string | string[]) {
    if (!user.loggedIn) return false
    if (!code) return true // 只要求登录
  }

  return { has, loggedIn: computed(() => user.loggedIn) }
}
