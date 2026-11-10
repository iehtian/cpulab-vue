<template>
  <el-header>
    <el-menu
      class="el-menu-demo"
      :ellipsis="false"
      mode="horizontal"
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
          src="@/assets/科研管理.svg"
      /></el-menu-item>
      <el-sub-menu
        index="device"
        :popper-offset="0"
      >
        <template #title>仪器设备</template>
        <el-menu-item index="/reservation">设备预约</el-menu-item>
      </el-sub-menu>
      <el-sub-menu
        index="user"
        :popper-offset="0"
      >
        <template #title>个人中心</template>
        <el-menu-item
          v-if="!userStore.loggedIn"
          index="/register"
          >注册</el-menu-item
        >
        <el-menu-item
          v-if="!userStore.loggedIn"
          index="/login"
          >登录</el-menu-item
        >
        <el-menu-item
          v-if="userStore.loggedIn"
          index="/logout"
          >退出登录</el-menu-item
        >
      </el-sub-menu>
    </el-menu>
  </el-header>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user.ts'

defineProps({
  menuKey: {
    type: String,
    default: '',
  },
})
const emit = defineEmits(['update:menuKey'])

const userStore = useUserStore()

const handleSelect = (key: string) => {
  emit('update:menuKey', key)
}
</script>

<style scoped>
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
