<template>
    <div class="user">
        <span>姓名：{{ user.name }}</span>
        <span>手机号：{{ user.phone }}</span>
        <span>邮箱：{{ user.email }}</span>

    </div>
</template>

<script setup lang="ts">

    import { ref } from 'vue'

    const user = ref({
        name: '张三',
        phone: '13800000000',
        email: 'zhangsan@example.com',
    })

</script>

<style scoped>
    .user {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
</style>
