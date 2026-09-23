<template>
  <el-container>
    <el-header>
      <el-menu :default-active="activeIndex" class="el-menu-demo" :ellipsis="false" mode="horizontal"
        @select="handleSelect">
        <el-menu-item index="/" class="logo-menu-item">
          <img alt="Vue logo" style="width: 30px; height: 30px" class="logo" src="./assets/科研管理.svg" /></el-menu-item>
        <el-sub-menu index="device" :popper-offset="0">
          <template #title>设备预约</template>
          <el-menu-item index="/Cell-room">细胞房</el-menu-item>
          <el-sub-menu index="dev" :popper-offset="0">
            <template #title>设备预约</template>
            <el-menu-item index="/Cell-roo">细胞房</el-menu-item>
          </el-sub-menu>
        </el-sub-menu>
        <el-sub-menu index="user" :popper-offset="0">
          <template #title>个人中心</template>
          <el-menu-item v-if="!checkStore.loggedIn" index="/register">注册</el-menu-item>
          <el-menu-item v-if="!checkStore.loggedIn" index="/login">登录</el-menu-item>
          <el-menu-item v-if="checkStore.loggedIn" index="/logout">退出登录</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-header>

    <el-container>
      <el-aside width="200px"></el-aside>
      <el-main>
        <RouterView />
      </el-main>
      <el-aside width="200px"></el-aside>
    </el-container>
  </el-container>

  <Regiester v-model:visible="RegiesterVisible" />
  <Login v-model:visible="LoginVisible" />
</template>

<script setup lang="ts">
  import { RouterLink, RouterView } from 'vue-router'
  import HelloWorld from './components/HelloWorld.vue'
  import ButtonExample from './components/button.vue'
  import OnedayExample from './components/oneday.vue'
  import Regiester from './components/Regiester.vue'
  import { ref } from 'vue'
  import router from './router/index.ts'
  import Login from '@/components/Login.vue'

  const activeIndex = ref('1')
  const RegiesterVisible = ref(false)
  const LoginVisible = ref(false)

  const handleSelect = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
    activeIndex.value = key
    if (key === '/Cell-room') {
      router.push('/Cell-room')
    } else if (key === '/User') {
      router.push('/User')
    } else if (key === '/register') {
      RegiesterVisible.value = true
    } else if (key === '/login') {
      LoginVisible.value = true
    } else if (key === '/logout') {
      checkStore.logout()
    }
  }
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

  .el-menu--horizontal>.el-menu-item:nth-child(1) {
    margin-right: auto;
  }

  /* 取消 Logo 菜单项点击后的激活高亮（主题色文字与底部边框） */
  .el-menu--horizontal>.logo-menu-item.is-active {
    color: var(--el-menu-text-color);
    border-bottom-color: transparent;
  }

  .el-menu--horizontal>.logo-menu-item:hover,
  .el-menu--horizontal>.logo-menu-item:focus {
    color: var(--el-menu-text-color);
    background-color: transparent;
  }
</style>
