import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomePage.vue'),
      meta: {
        title: '首页',
        isTabPage: true,
      },
    },
    {
      path: '/cell-room',
      name: 'CellRoom',
      component: () => import('../views/CellRoom.vue'),
      meta: {
        title: '标签',
        isTabPage: true,
      },
    },
    {
      path: '/user',
      name: 'User',
      component: () => import('../views/MobileUser.vue'),
      meta: {
        title: '我的',
        isTabPage: true,
      },
    },
    {
      path: '/manager',
      name: 'Manager',
      component: () => import('../views/Manager.vue'),
      meta: {
        title: '试剂',
        isTabPage: true,
      },
    },
    {
      path: '/spaces/:id',
      name: 'Spaces',
      component: () => import('../views/Spaces.vue'),
      meta: {
        title: '空间详情',
      },
    },
    {
      path: '/restock',
      name: 'Restock',
      component: () => import('../views/ReagentRestock.vue'),
      meta: {
        title: '补货',
      },
    },
    {
      path: '/oauth/authorize',
      name: 'OAuthAuthorize',
      component: () => import('../views/OAuthAuthorize.vue'),
      meta: {
        title: '授权确认',
      },
    },
  ],
})

export default router
