<template>
  <!-- <el-container
    direction="vertical"
    v-if="!isMobile"
  >
    <AppHeader v-model:menu-key="currentKey" />
    <el-container>
      <el-aside
        v-if="!isMobile"
        width="150px"
      ></el-aside>
      <el-main>
        <RouterView />
      </el-main>
      <el-aside
        v-if="!isMobile"
        width="150px"
      ></el-aside>
    </el-container>
    <RegisterDialog v-model:visible="showRegisterDialog" />
    <LoginDialog v-model:visible="showLoginDialog" />
  </el-container> -->

  <van-nav-bar
    :title="pageTitle"
    :left-text="isTabPage ? '' : '返回'"
    :left-arrow="!isTabPage"
    @click-left="onClickLeft"
  />
  <router-view />
  <van-tabbar route>
    <van-tabbar-item
      replace
      to="/home"
      icon="home-o"
      >首页</van-tabbar-item
    >
    <van-tabbar-item
      replace
      to="/devices"
      icon="calendar-o"
      >仪器</van-tabbar-item
    >
    <van-tabbar-item
      replace
      to="/manager"
      icon="cluster-o"
      >试剂</van-tabbar-item
    >
    <van-tabbar-item
      replace
      to="/user"
      icon="user-o"
      >用户</van-tabbar-item
    >
  </van-tabbar>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useRoute } from 'vue-router'
import router from './router/index.ts'
import AppHeader from '@/components/AppHeader.vue'
import RegisterDialog from '@/components/RegisterDialog.vue'
import LoginDialog from '@/components/LoginDialog.vue'
import { useViewportStore } from '@/stores/viewport.ts'
import { useUserStore } from '@/stores/user.ts'

const viewportStore = useViewportStore()
const userStore = useUserStore()
const route = useRoute()
const isMobile = viewportStore.isMobile
const pageTitle = computed(() => {
  const title = route.meta.title
  // 支持函数形式的标题（如设备详情页按路由参数显示设备名）
  if (typeof title === 'function') {
    return (title as (r: typeof route) => string)(route)
  }
  return typeof title === 'string' ? title : 'CPU 实验室管理平台'
})
const isTabPage = computed(() => route.meta.isTabPage === true)

const showRegisterDialog = ref(false)
const showLoginDialog = ref(false)
const currentKey = ref('')
watch(currentKey, (newKey) => {
  if (newKey === '/reservation') {
    router.push('/reservation')
  } else if (newKey === '/user') {
    router.push('/user')
  } else if (newKey === '/register') {
    showRegisterDialog.value = true
  } else if (newKey === '/login') {
    showLoginDialog.value = true
  } else if (newKey === '/logout') {
    userStore.logout()
  }
})

const onClickLeft = () => history.back()
</script>

<style scoped>
.el-aside {
  background-color: #f5f7fa;
}

.register-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
</style>
