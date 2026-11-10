import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalizedLoaded } from 'vue-router'
import { getDeviceById } from '@/config/devices'

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
      path: '/devices',
      name: 'DeviceList',
      component: () => import('../views/DeviceList.vue'),
      meta: {
        title: '仪器',
        isTabPage: true,
      },
    },
    {
      path: '/devices/:deviceId',
      name: 'Device',
      component: () => import('../views/DeviceMobile.vue'),
      meta: {
        title: (route: RouteLocationNormalizedLoaded) =>
          getDeviceById(String(route.params.deviceId))?.name ?? '设备预约',
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
      path: '/common-used',
      name: 'CommonUsed',
      component: () => import('../views/CommonUsedReagents.vue'),
      meta: {
        title: '常用试剂',
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
