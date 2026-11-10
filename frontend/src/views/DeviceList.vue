<template>
  <div class="device-list-page">
    <div
      v-loading="refreshing"
      class="device-list"
    >
      <el-card
        v-for="device in DEVICES"
        :key="device.id"
        class="device-card"
        :class="{ disabled: !device.enabled }"
        shadow="hover"
        :body-style="{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }"
        @click="goDevice(device)"
      >
        <div class="card-top">
          <component
            :is="device.icon"
            :size="28"
          />
          <el-tag
            v-if="!device.enabled"
            type="warning"
            >维护中</el-tag
          >
          <el-tag
            v-else-if="isFull(device)"
            type="danger"
            >今日已约满</el-tag
          >
          <el-tag
            v-else
            type="success"
            effect="plain"
            >可预约</el-tag
          >
        </div>
        <div class="device-name">{{ device.name }}</div>
        <div class="device-desc">{{ device.description }}</div>
        <div class="device-stats">
          今日已约 {{ bookedCount(device.id) }}/{{ device.totalSlots }} 时段
        </div>
      </el-card>
    </div>

    <el-empty
      v-if="DEVICES.length === 0"
      description="暂无可预约设备"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DEVICES } from '@/config/devices'
import type { DeviceInfo } from '@/config/devices'
import { getBookings } from '@/api/booking'
import { dateStr } from '@/utils/date'

const router = useRouter()

const refreshing = ref(false)
/** 各设备今日已约时段数，key 为设备 id */
const todayStats = ref<Record<string, number>>({})

function bookedCount(id: string): number {
  return todayStats.value[id] ?? 0
}

function isFull(device: DeviceInfo): boolean {
  return bookedCount(device.id) >= device.totalSlots
}

function goDevice(device: DeviceInfo) {
  if (!device.enabled) {
    ElMessage.warning('设备维护中，暂不可预约')
    return
  }
  router.push(`/devices/${device.id}`)
}

async function fetchStats() {
  refreshing.value = true
  const today = dateStr(new Date())
  await Promise.all(
    DEVICES.map(async (device) => {
      const bookings = await getBookings(device.id, today)
      todayStats.value[device.id] = Object.keys(bookings).length
    }),
  )
  refreshing.value = false
}

onMounted(fetchStats)
</script>

<style scoped>
.device-list-page {
  padding: 12px;
}

.device-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.device-card {
  border-radius: 8px;
  cursor: pointer;
}

.device-card.disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-name {
  font-size: 16px;
  font-weight: 600;
}

.device-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.device-stats {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  border-top: 1px dashed var(--el-border-color);
  padding-top: 6px;
}
</style>
