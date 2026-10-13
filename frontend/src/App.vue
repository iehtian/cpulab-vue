<template>
  <el-container
    direction="vertical"
    v-if="!isMobile"
  >
    <Title v-model:key="currentKey" />
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
    <Regiester v-model:visible="RegiesterVisible" />
    <Login v-model:visible="LoginVisible" />
  </el-container>
  <van-nav-bar title="标题" />
<router-view />
  <van-tabbar route>
    <van-tabbar-item
      replace
      to="/Cell-room"
      icon="home-o"
      >标签</van-tabbar-item
    >  
        <van-tabbar-item
      replace
      to="/User"
      icon="search"
      >标签</van-tabbar-item
    >  
  </van-tabbar>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Regiester from './components/Regiester.vue'
import { ref, watch } from 'vue'
import router from './router/index.ts'
import Login from '@/components/Login.vue'
import { useViewportStore } from '@/stores/viewport.ts'
import Title from '@/components/Title.vue'

const viewportStore = useViewportStore()
const isMobile = viewportStore.isMobile

const RegiesterVisible = ref(false)
const LoginVisible = ref(false)
const currentKey = ref('')
watch(currentKey, (newKey) => {
  if (newKey === '/Cell-room') {
    router.push('/Cell-room')
  } else if (newKey === '/User') {
    router.push('/User')
  } else if (newKey === '/register') {
    RegiesterVisible.value = true
  } else if (newKey === '/login') {
    LoginVisible.value = true
  } else if (newKey === '/logout') {
    checkStore.logout()
  }
})

import { useCheckStore } from './stores/user.ts'
const checkStore = useCheckStore()
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
