<template>
  <el-container direction="vertical">
    <!-- <el-header v-if="!isMobile">
      <el-menu
        class="el-menu-demo"
        :ellipsis="false"
        mode="horizontal"
        @select="handleSelect"
        :menu-trigger="isMobile ? 'click' : 'hover'"
      >
        <el-menu-item
          index="/"
          class="logo-menu-item"
        >
          <img
            alt="Vue logo"
            style="width: 30px; height: 30px"
            class="logo"
            src="./assets/科研管理.svg"
        /></el-menu-item>
        <el-sub-menu
          index="device"
          :popper-offset="0"
        >
          <template #title>仪器设备</template>
          <el-menu-item index="/Cell-room">细胞房</el-menu-item>
        </el-sub-menu>
        <el-sub-menu
          index="user"
          :popper-offset="0"
        >
          <template #title>个人中心</template>
          <el-menu-item
            v-if="!checkStore.loggedIn"
            index="/register"
            >注册</el-menu-item
          >
          <el-menu-item
            v-if="!checkStore.loggedIn"
            index="/login"
            >登录</el-menu-item
          >
          <el-menu-item
            v-if="checkStore.loggedIn"
            index="/logout"
            >退出登录</el-menu-item
          >
        </el-sub-menu>
      </el-menu>
    </el-header> -->

    <Title v-model:key="currentKey" />
    <el-container>
      <el-aside
        v-if="!isMobile"
        width="150px"
      ></el-aside>
      <el-main>
        <!-- <RouterView /> -->
      </el-main>
      <el-aside
        v-if="!isMobile"
        width="150px"
      ></el-aside>
    </el-container>
  </el-container>

  <Regiester v-model:visible="RegiesterVisible" />
  <Login v-model:visible="LoginVisible" />
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
