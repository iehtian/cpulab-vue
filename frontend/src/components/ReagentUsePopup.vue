<template>
  <van-dialog
    v-model:show="visible"
    title="提示"
    show-cancel-button
    confirm-button-text="确定"
    :confirm-button-disabled="!isUsageValid"
    @confirm="handleConfirm"
  >
    <van-field
      v-model="usageInput"
      type="digit"
      label="记录用量"
      placeholder="请输入用量（ml）"
      :formatter="onlyNumber"
    />
  </van-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const emit = defineEmits<{ confirm: [value: string] }>()
const visible = defineModel<boolean>('show', { required: true })
const usageInput = defineModel<string>('value', { default: '' })

const handleConfirm = () => {
  emit('confirm', usageInput.value)
  usageInput.value = ''
}

const isUsageValid = computed(() => {
  const n = Number(usageInput.value)
  return usageInput.value !== '' && Number.isFinite(n) && n > 0
})

const onlyNumber = (value: string) => value.replace(/[^\d]/g, '')
</script>
