import { useMediaQuery } from '@vueuse/core'
import { defineStore } from 'pinia'

export const useViewportStore = defineStore('viewport', () => {
  const isMobile = useMediaQuery('(max-width: 768px)')
  return { isMobile }
})
