import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/cell-room',
      name: 'CellRoom',
      component: () => import('../views/CellRoom.vue'),
    },
    {
      path: '/user',
      name: 'User',
      component: () => import('../views/MobileUser.vue'),
    },
    {
      path: '/manager',
      name: 'Manager',
      component: () => import('../views/Manager.vue'),
    },
    {
      path: '/spaces/:id',
      name: 'Spaces',
      component: () => import('../views/Spaces.vue'),
    },
  ],
})

export default router
