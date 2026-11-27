// directives/permission.ts
import type { Directive } from 'vue'
import { usePermission } from '@/composables/usePermission'

export const permission: Directive<HTMLElement, string | string[] | undefined> = {
  mounted(el, binding) {
    if (!usePermission().has(binding.value)) el.remove()
  },
}
