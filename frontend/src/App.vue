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
      to="/cell-room"
      icon="home-o"
      >标签</van-tabbar-item
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
  return typeof route.meta.title === 'string' ? route.meta.title : 'CPU 实验室管理平台'
})
const isTabPage = computed(() => route.meta.isTabPage === true)

const showRegisterDialog = ref(false)
const showLoginDialog = ref(false)
const currentKey = ref('')
watch(currentKey, (newKey) => {
  if (newKey === '/cell-room') {
    router.push('/cell-room')
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
