<template>
    <div>
        <el-checkbox-group class="title" v-model="checkboxGroup1" size="large">
            <el-checkbox-button v-for="city in cities" :key="city" :value="city">
                {{ city }}
            </el-checkbox-button>
        </el-checkbox-group>
    </div>
    <div class="demo-button-style">
        <el-checkbox-group class="container" v-model="checkboxGroup2">
            <el-checkbox-button v-for="city in cities" :key="city" :value="city">
                {{ city }}
            </el-checkbox-button>
        </el-checkbox-group>
    </div>
</template>

<script lang="ts" setup>
    import { ref } from 'vue'

    const checkboxGroup1 = ref(['Shanghai'])
    const checkboxGroup2 = ref(['Shanghai'])
    const cities = ['Shanghai', 'Beijing', 'Guangzhou', 'Shenzhen']
</script>

<style scoped>

    :deep(.el-checkbox-group.container) {
        display: inline-flex;
        flex-direction: column;
        align-items: stretch;
    }

    :deep(.el-checkbox-button.container) {
        display: block;
        margin-left: 0 !important;
    }

    :deep(.el-checkbox-button__inner.container) {
        display: block;
        border-left: 1px solid var(--el-border) !important;
        border-radius: 0 !important;
        margin-left: 0 !important;
    }

    :deep(.el-checkbox-button:not(:first-child) .el-checkbox-button__inner.container) {
        margin-top: -1px;
    }

    :deep(.el-checkbox-button:first-child .el-checkbox-button__inner.container) {
        border-top-left-radius: var(--el-border-radius-base) !important;
        border-top-right-radius: var(--el-border-radius-base) !important;
    }

    :deep(.el-checkbox-button:last-child .el-checkbox-button__inner.container) {
        border-bottom-left-radius: var(--el-border-radius-base) !important;
        border-bottom-right-radius: var(--el-border-radius-base) !important;
    }
</style>