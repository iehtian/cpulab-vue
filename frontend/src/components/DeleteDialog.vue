<template>
  <van-dialog
    v-model:show="visible"
    title="确认删除"
    :message="message"
    confirm-button-text="删除"
    cancel-button-text="取消"
    show-cancel-button
    @confirm="emit('confirm')"
  />
</template>

<script setup lang="ts">
const visible = defineModel<boolean>('visible')
withDefaults(defineProps<{ message?: string }>(), {
  message: '删除后无法恢复，是否继续？',
})
const emit = defineEmits<{
  confirm: []
}>()
</script>
