<template>
  <div class="device-reservation">
    <el-card>...</el-card>
    <el-affix
      :offset="20"
      position="bottom"
    >
      <div class="reservation-footer">
        <el-tag type="primary">{{ selectedSlot.length }}个预约</el-tag>
        <el-button
          type="primary"
          @click="emit('confirm')"
        >
          {{ text }}</el-button
        >
      </div>
    </el-affix>
  </div>
</template>

<script setup lang="ts">
defineProps({
  selectedSlot: {
    type: Array,
    default: () => [],
  },
  onConfirm: {
    type: Function,
    default: () => {},
  },
  text: {
    type: String,
    default: '确认预约',
  },
})
const emit = defineEmits(['confirm'])
</script>
