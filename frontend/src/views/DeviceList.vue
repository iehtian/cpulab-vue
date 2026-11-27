<template>
  <div class="device-list">
    <div
      v-for="device in DEVICES"
      :key="device.id"
      class="device-card"
      :class="{ disabled: !device.enabled }"
      @click="goDevice(device)"
    >
      <div class="card-top">
        <van-tag
          v-if="!device.enabled"
          type="warning"
          >维护中</van-tag
        >
        <van-tag
          v-else
          type="primary"
          plain
          >可预约</van-tag
        >
      </div>
      <div class="device-name">{{ device.name }}</div>
      <div class="device-desc">{{ device.description }}</div>
    </div>
  </div>
  <van-empty
    v-if="DEVICES.length === 0"
    description="暂无可预约设备"
  />
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { DEVICES } from '@/config/devices'
import type { DeviceInfo } from '@/config/devices'

const router = useRouter()

function goDevice(device: DeviceInfo) {
  if (!device.enabled) {
    showToast('设备维护中，暂不可预约')
    return
  }
  router.push(`/devices/${device.id}`)
}
</script>

<style scoped>
.device-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 12px;
}

.device-card {
  background: var(--van-background-2, #fff);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.device-card:active {
  background: var(--van-active-color);
}

.device-card.disabled {
  opacity: 0.55;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-icon {
  font-size: 28px;
}

.device-name {
  font-size: 16px;
  font-weight: 600;
}

.device-desc {
  font-size: 12px;
  color: var(--van-text-color-2, #969799);
}
</style>
