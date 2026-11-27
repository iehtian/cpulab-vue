import type { permission } from './permission.ts'

declare module 'vue' {
  interface GlobalDirectives {
    vPermission: typeof permission
  }
}
