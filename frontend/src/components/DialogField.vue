<template>
  <van-dialog
    v-model:show="show"
    :title="title"
    show-cancel-button
    :before-close="beforeClose"
  >
    <van-field
      v-model="inputValue"
      :label="label"
      :placeholder="placeholder"
    />
  </van-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  label: { type: String, default: '' },
  initialValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
})

const emit = defineEmits<{
  (e: 'confirm', value: string): void
}>()

const show = defineModel<boolean>({ default: false })

// 受控的输入值 + 初始值（编辑场景可回显）
const inputValue = ref('')
watch(show, (v) => {
  if (v) inputValue.value = props.initialValue
})

const beforeClose = (action: string) => {
  if (action === 'cancel') return true
  if (!inputValue.value.trim()) return false // 空值不关闭
  emit('confirm', inputValue.value)
  return true
}
</script>
