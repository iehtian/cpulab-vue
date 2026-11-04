<template>
    <div class="oauth-page">
        <el-card class="oauth-card">
            <template v-if="errorMessage">
                <el-result icon="error" title="授权请求无效" :sub-title="errorMessage" />
            </template>

            <template v-else>
                <div class="app-info">
                    <h2>{{ clientName || '加载中…' }}</h2>
                    <p>请求获取你的账号信息（用户名、邮箱、手机号）</p>
                </div>

                <div v-if="!userStore.loggedIn" class="login-hint">
                    <el-alert type="warning" :closable="false" title="登录后才能授权" show-icon />
                    <el-button type="primary" @click="loginVisible = true">去登录</el-button>
                </div>

                <div v-else class="actions">
                    <p class="current-user">当前账号：{{ userStore.userName }}</p>
                    <div class="buttons">
                        <el-button type="primary" :loading="submitting" @click="handleAgree">
                            同意授权
                        </el-button>
                        <el-button @click="handleDeny">拒绝</el-button>
                    </div>
                </div>
            </template>
        </el-card>

        <LoginDialog v-model:visible="loginVisible" />
    </div>
</template>

<script setup lang="ts">
    import { onMounted, ref } from 'vue'
    import { useRoute } from 'vue-router'
    import { ElMessage } from 'element-plus'
    import service from '@/utils/request'
    import { useUserStore } from '@/stores/user'
    import LoginDialog from '@/components/LoginDialog.vue'

    const route = useRoute()
    const userStore = useUserStore()

    const clientId = ref('')
    const redirectUri = ref('')
    const state = ref('')
    const clientName = ref('')
    const errorMessage = ref('')
    const loginVisible = ref(false)
    const submitting = ref(false)

    onMounted(async () => {
        clientId.value = String(route.query.client_id || '')
        redirectUri.value = String(route.query.redirect_uri || '')
        state.value = String(route.query.state || '')

        if (!clientId.value || !redirectUri.value) {
            errorMessage.value = '链接缺少 client_id 或 redirect_uri 参数'
            return
        }

        try {
            const res = await service.get('/api/oauth/client-info', {
                params: { client_id: clientId.value },
            })
            clientName.value = res.data.client_name
        } catch {
            errorMessage.value = '应用不存在或未注册'
            return
        }

        // 已有本地 token 则尝试恢复登录态；失败或未登录则弹出登录框
        if (localStorage.getItem('access_token')) {
            try {
                await userStore.checkAuth()
            } catch {
                /* 视为未登录 */
            }
        }
        if (!userStore.loggedIn) loginVisible.value = true
    })

    const handleAgree = async () => {
        submitting.value = true
        try {
            const res = await service.get('/api/oauth/authorize', {
                params: {
                    client_id: clientId.value,
                    redirect_uri: redirectUri.value,
                    state: state.value,
                },
            })
            // 后端不直接 302（避免 axios 跟随跨域重定向），由前端整页跳回第三方
            window.location.href = res.data.redirect
        } catch {
            ElMessage.error('授权失败，请重试')
        } finally {
            submitting.value = false
        }
    }

    const handleDeny = () => {
        // 按 OAuth 规范把 error 和 state 带回第三方回调地址
        const sep = redirectUri.value.includes('?') ? '&' : '?'
        const params = new URLSearchParams({ error: 'access_denied', state: state.value })
        window.location.href = `${redirectUri.value}${sep}${params.toString()}`
    }
</script>

<style scoped>
    .oauth-page {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f7fa;
    }

    .oauth-card {
        width: 420px;
        max-width: 90vw;
    }

    .app-info {
        text-align: center;
        margin-bottom: 24px;
    }

    .app-info h2 {
        margin: 0 0 8px;
    }

    .app-info p {
        color: #606266;
        margin: 0;
    }

    .login-hint {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
    }

    .actions {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
    }

    .current-user {
        color: #606266;
        margin: 0;
    }
</style>
