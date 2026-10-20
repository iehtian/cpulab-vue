<template>
  <van-dialog
    v-model:show="show"
    :title="title"
    show-cancel-button
    @confirm="onConfirm"
  >
    <van-field
      v-model="spaceName"
      label="空间名称"
      placeholder="请输入空间名称"
    />
  </van-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const props = defineProps({
  title: {
    type: String,
    default: '添加空间',
  },
  show: {
    type: Boolean,
    default: false,
  },
  onConfirm_it: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits(['update:show'])

const spaceName = ref('')
const onConfirm = () => {
  props.onConfirm_it(spaceName.value)
  spaceName.value = ''
  emit('update:show', false)
}
</script>
