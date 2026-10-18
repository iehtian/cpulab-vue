import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/Cell-room',
      name: 'Cell-room',
      component: () => import('../views/CellRoom.vue'),
    },
    {
      path: '/User',
      name: 'User',
      component: () => import('../views/MobileUser.vue'),
    },
    {
      path: '/Manager',
      name: 'Manager',
      component: () => import('../views/Manager.vue'),
    },
    {
      path: '/Spaces',
      name: 'Spaces',
      component: () => import('../views/Spaces.vue'),
    },
  ],
})

export default router
