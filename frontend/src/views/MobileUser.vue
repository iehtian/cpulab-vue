<template>
  <div class="user-page">
    <van-nav-bar title="我的" />

    <!-- 已登录 -->
    <template v-if="checkStore.loggedIn">
      <van-cell-group inset class="user-card">
        <van-cell title="用户名" :value="displayName" />
      </van-cell-group>
      <div class="btn-area">
        <van-button round block type="danger" @click="checkStore.logout()">
          退出登录
        </van-button>
      </div>
    </template>

    <!-- 未登录：单表单，登录/注册模式切换 -->
    <div v-else class="form-card">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="username"
            name="username"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请填写用户名' }]"
          />
          <van-field
            v-model="password"
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请填写密码' }]"
          />
          <van-field
            v-if="isRegister"
            v-model="email"
            name="email"
            label="邮箱"
            placeholder="请输入邮箱"
            :rules="[
              { required: true, message: '请填写邮箱' },
              { pattern: emailPattern, message: '邮箱格式不正确' },
            ]"
          />
        </van-cell-group>
        <div class="btn-area">
          <van-button round block type="primary" native-type="submit">
            {{ isRegister ? '注册并登录' : '登录' }}
          </van-button>
          <div class="switch-link" @click="toggleMode">
            {{ isRegister ? '已有账号？返回登录' : '没有账号？立即注册' }}
          </div>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { showFailToast, showSuccessToast } from 'vant'
import { useCheckStore } from '@/stores/user.ts'

const checkStore = useCheckStore()

const isRegister = ref(false)
const username = ref('')
const password = ref('')
const email = ref('')

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const displayName = computed(() => {
  const info = checkStore.userInfo as { user_name?: string } | null
  return info?.user_name ?? '已登录用户'
})

function toggleMode() {
  isRegister.value = !isRegister.value
}

async function onSubmit() {
  try {
    if (isRegister.value) {
      await checkStore.register(username.value, email.value, '', password.value)
      showSuccessToast('注册成功')
    } else {
      await checkStore.login(username.value, password.value)
      showSuccessToast('登录成功')
    }
  } catch (error) {
    console.error(isRegister.value ? '注册失败:' : '登录失败:', error)
    showFailToast(isRegister.value ? '注册失败，请稍后重试' : '登录失败，请检查用户名或密码')
  }
}
</script>

<style scoped>
.user-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.form-card {
  margin-top: 24px;
  padding-top: 16px;
}

.btn-area {
  margin: 24px 16px 0;
}

.switch-link {
  margin-top: 16px;
  text-align: center;
  color: #1989fa;
  font-size: 14px;
}

.user-card {
  margin-top: 16px;
}
</style>
