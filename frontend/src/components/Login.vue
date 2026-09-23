<template>
    <el-dialog v-model="dialogVisible" title="注册" width="500" align-center>
        <div class="register-form">
            <el-input v-model="username" style="width: 240px" placeholder="请输入用户名" />
            <el-input v-model="password" style="width: 240px" type="password" placeholder="请输入密码" show-password />

        </div>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="emit('update:visible', false)">Cancel</el-button>
                <el-button type="primary" @click="handleLogin">
                    Confirm
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import { useCheckStore } from '@/stores/user'
    const checkStore = useCheckStore()



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
            await checkStore.login(
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
    .register-form {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }
</style>
