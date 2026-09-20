<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import ButtonExample from './components/button.vue'
import OnedayExample from './components/oneday.vue'

import { ref } from 'vue'
import { el } from 'element-plus/es/locales.mjs'

const activeIndex = ref('1')

const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
</script>

<template>
  <el-container>
    <el-header>
      <el-menu
        :default-active="activeIndex"
        class="el-menu-demo"
        :ellipsis="false"
        mode="horizontal"
        router
        @select="handleSelect"
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
        <el-sub-menu>
          <template #title>设备预约</template>
          <el-menu-item index="/Cell-room">细胞房</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/User">个人中心</el-menu-item>
      </el-menu>
    </el-header>

    <el-container>
      <el-aside width="200px"></el-aside>
      <el-main>
        <!-- <div class="wrapper">
      <nav>
        <RouterLink to="/reservation">设备预约</RouterLink>
        <RouterLink to="/DeviceReservation_bak">设备预约备份</RouterLink>
      </nav>
    </div> -->
        <RouterView />
      </el-main>
      <el-aside width="200px"></el-aside>
    </el-container>
  </el-container>
</template>

<style scoped>
.el-aside {
  background-color: #f5f7fa;
}

.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

/* 取消 Logo 菜单项点击后的激活高亮（主题色文字与底部边框） */
.el-menu--horizontal > .logo-menu-item.is-active {
  color: var(--el-menu-text-color);
  border-bottom-color: transparent;
}

.el-menu--horizontal > .logo-menu-item:hover,
.el-menu--horizontal > .logo-menu-item:focus {
  color: var(--el-menu-text-color);
  background-color: transparent;
}
</style>
