<template>
  <van-dialog
    v-model:show="showUsageDialog"
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
import { ref, computed } from 'vue'
const emit = defineEmits<{ confirm: [vale: string] }>()
const showUsageDialog = defineModel<boolean>('show', { required: true })

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
