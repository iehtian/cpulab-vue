<template>
    <el-dialog v-model="dialogVisible" title="登录" width="500" align-center>
        <div class="login-form">
            <el-input v-model="username" style="width: 240px" placeholder="请输入用户名" />
            <el-input v-model="password" style="width: 240px" type="password" placeholder="请输入密码" show-password />

        </div>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="emit('update:visible', false)">取消</el-button>
                <el-button type="primary" @click="handleLogin">
                    登录
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import { useUserStore } from '@/stores/user'
    const userStore = useUserStore()



    const props = defineProps({
        visible: {
            type: Boolean,
            default: false
        }
    })
    const emit = defineEmits(['update:visible'])
    const dialogVisible = computed({
        get: () => props.visible, // 读 → 透传父状态 
        set: (v) => emit('update:visible', v) // 写 → 转发回父组件 
    })
    const username = ref('')
    const password = ref('')

    const handleLogin = async () => {
        try {
            await userStore.login(
                username.value,
                password.value
            )
            dialogVisible.value = false
        } catch (error) {
            console.error('登录失败:', error)
        }
    }
</script>

<style scoped>
    .login-form {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }
</style>
