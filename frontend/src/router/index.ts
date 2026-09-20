import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/Cell-room',
      name: 'Cell-room',
      component: () => import('../views/DeviceReservation.vue'),
    },
    {
      path: '/User',
      name: 'User',
      component: () => import('../views/User.vue'),
    },
    {
      path: '/DeviceReservation_bak',
      name: 'DeviceReservation_bak',
      component: () => import('../views/DeviceReservation_bak.vue'),
    },
  ],
})

export default router
