<template>
  <van-dialog
    v-model:show="visible"
    title="确认删除"
    message="删除后无法恢复，是否继续？"
    confirm-button-text="删除"
    cancel-button-text="取消"
    show-cancel-button
    @confirm="emit('confirm')"
  />
</template>

<script setup lang="ts">
const visible = defineModel<boolean>('visible')
const emit = defineEmits<{
  confirm: []
}>()
</script>
