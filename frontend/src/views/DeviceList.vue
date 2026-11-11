<template>
  <van-pull-refresh
    v-model="refreshing"
    @refresh="fetchStats"
  >
    <div class="device-list">
      <div
        v-for="device in DEVICES"
        :key="device.id"
        class="device-card"
        :class="{ disabled: !device.enabled }"
        @click="goDevice(device)"
      >
        <div class="card-top">
          <span class="device-icon"
            ><component
              :is="device.icon"
              :size="28"
          /></span>
          <van-tag
            v-if="!device.enabled"
            type="warning"
            >维护中</van-tag
          >
          <van-tag
            v-else-if="isFull(device)"
            type="danger"
            >今日已约满</van-tag
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
        <div class="device-stats">
          今日剩余可约 {{ remainingCount(device) }}/{{ device.totalSlots }} 时段
        </div>
      </div>
    </div>
    <van-empty
      v-if="DEVICES.length === 0"
      description="暂无可预约设备"
    />
  </van-pull-refresh>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { DEVICES } from '@/config/devices'
import type { DeviceInfo } from '@/config/devices'
import { getBookings } from '@/api/booking'
import type { BookingInfo } from '@/api/booking'
import { firstFutureSlotIndex } from '@/composables/useSlotTime'
import { dateStr } from '@/utils/date'

const router = useRouter()

const refreshing = ref(false)
/** 各设备今日预约记录（槽位 id → 预约信息），key 为设备 id */
const todayStats = ref<Record<string, Record<number, BookingInfo>>>({})

/** 今日剩余可约时段数 = 尚未开始的槽位数 − 其中已被预约的数量 */
function remainingCount(device: DeviceInfo): number {
  const first = firstFutureSlotIndex(device.totalSlots)
  const futureSlots = device.totalSlots - first
  const bookings = todayStats.value[device.id] ?? {}
  const bookedFuture = Object.keys(bookings).filter((k) => Number(k) >= first).length
  return Math.max(futureSlots - bookedFuture, 0)
}

function isFull(device: DeviceInfo): boolean {
  return remainingCount(device) <= 0
}

function goDevice(device: DeviceInfo) {
  if (!device.enabled) {
    showToast('设备维护中，暂不可预约')
    return
  }
  router.push(`/devices/${device.id}`)
}

async function fetchStats() {
  const today = dateStr(new Date())
  await Promise.all(
    DEVICES.map(async (device) => {
      todayStats.value[device.id] = await getBookings(device.id, today)
    }),
  )
  refreshing.value = false
}

onMounted(fetchStats)
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

.device-stats {
  font-size: 12px;
  color: var(--van-text-color-2, #969799);
  border-top: 1px dashed var(--van-border-color, #ebedf0);
  padding-top: 6px;
}
</style>
