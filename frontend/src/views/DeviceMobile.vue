<template>
  <div
    class="mobile-booking"
    :class="{ 'has-action-bar': hasSelection }"
  >
    <div>
      <van-cell
        class="date-cell"
        :value="dateStr(date)"
        @click="showCalendar = true"
      >
        <template #icon>
          <van-button
            size="small"
            @click.stop="changeSelectedDate(-1)"
          >
            前一天
          </van-button>
        </template>

        <template #right-icon>
          <van-button
            size="small"
            @click.stop="changeSelectedDate(1)"
          >
            后一天
          </van-button>
        </template>
      </van-cell>
      <van-cell>
        <template #icon> 今日值日生 {{ duty[0] }}</template>
      </van-cell>
      <van-calendar
        v-model:show="showCalendar"
        :show-confirm="false"
        @confirm="onDateConfirm"
      />
    </div>

    <van-grid
      :column-num="4"
      clickable
    >
      <van-grid-item
        v-for="id of devicesInfo?.totalSlots ?? 0"
        :key="id"
        class="booking-slot"
        :class="{
          ispast: isPastBlock({ date: 0, id: id - 1 }),
          selected: isSelected({ date: 0, id: id - 1 }),
        }"
        :style="{ '--slot-bg': dayBookings?.[id - 1]?.color }"
        @click="toggleSelect(id - 1)"
      >
        <span class="slot-time">
          {{ dayBookings?.[id - 1]?.user_name ?? timeLabels.at(id - 1) }}
        </span>
      </van-grid-item>
    </van-grid>
    <div
      v-if="hasSelection"
      class="action-bar"
    >
      <van-button
        type="primary"
        v-if="bookingSlots.length > 0"
        @click="submit"
        >提交预约</van-button
      >
      <van-button
        type="danger"
        v-if="cancelingSlots.length > 0"
        @click="cancel"
        >取消预约</van-button
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import { changeDate, dateStr, getMonday } from '@/utils/date'
import { useSlotTime } from '@/composables/useSlotTime'
import { useReservation } from '@/composables/useReservation'
import { getDeviceById } from '@/config/devices'
import { useUserStore } from '@/stores/user'
import { getDutyLog } from '@/api/duty'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const devicesInfo = computed(() => getDeviceById(deviceId.value))

const duty = ref([])

async function fetchDuty() {
  if (!devicesInfo.value) return
  duty.value = await getDutyLog(devicesInfo.value.id, dateStr(getMonday(date.value)))
  console.log('duty', duty.value)
}

// 设备 ID 来自路由参数；未知设备直接退回列表页
const deviceId = computed(() => String(route.params.deviceId))
if (!getDeviceById(deviceId.value)) {
  showToast('设备不存在')
  router.replace('/reservation')
}

const date = ref(new Date())
const showCalendar = ref(false)

const { bookingSlots, cancelingSlots, dayBookings, submit, cancel } = useReservation(deviceId, date)

const dateList = computed(() => [date.value])
const { isPastBlock, isSelected, makeTimeLabels } = useSlotTime(
  dateList,
  bookingSlots,
  cancelingSlots,
)

const timeLabels = computed(() => makeTimeLabels(devicesInfo.value?.totalSlots ?? 0))

const hasSelection = computed(
  () => bookingSlots.value.length > 0 || cancelingSlots.value.length > 0,
)

function toggleBookingSlot(id: number) {
  const index = bookingSlots.value.indexOf(id)
  if (index === -1) {
    bookingSlots.value.push(id)
  } else {
    bookingSlots.value.splice(index, 1)
  }
}

function toggleCancelingSlot(id: number) {
  const index = cancelingSlots.value.indexOf(id)
  if (index === -1) {
    cancelingSlots.value.push(id)
  } else {
    cancelingSlots.value.splice(index, 1)
  }
}

function isBookedByOther(id: number) {
  if (dayBookings.value.hasOwnProperty(id)) {
    return dayBookings.value[id]?.user_name !== userStore.userName
  }
  return false
}

function isOwnBooking(id: number) {
  if (dayBookings.value.hasOwnProperty(id)) {
    return dayBookings.value[id]?.user_name === userStore.userName
  }
  return false
}

function toggleSelect(id: number) {
  if (!userStore.loggedIn || isPastBlock({ date: 0, id: id }) || isBookedByOther(id)) {
    return
  }
  if (isOwnBooking(id)) {
    toggleCancelingSlot(id)
  } else {
    toggleBookingSlot(id)
  }
}

const onDateConfirm = (selectedDate: Date) => {
  date.value = selectedDate
  showCalendar.value = false
}

function changeSelectedDate(offset: number) {
  date.value = changeDate(date.value, offset)
}

onMounted(fetchDuty)
</script>

<style scoped>
:deep(.date-cell .van-cell__value) {
  text-align: center;
}

.booking-slot :deep(.van-grid-item__content) {
  background: var(--slot-bg, #effaf3);
  height: 70px;
  padding: 4px;
}

.booking-slot.selected :deep(.van-grid-item__content) {
  background: var(--el-color-primary);
}

.slot-time {
  font-size: 14px;
}

/* 操作栏悬浮时给页面底部留空，避免遮住最后一排 */
.mobile-booking.has-action-bar {
  padding-bottom: 72px;
}

.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  /* 悬浮在固定 tabbar 上方 */
  bottom: calc(var(--van-tabbar-height, 50px) + env(safe-area-inset-bottom));
  z-index: 10;
  display: flex;
  gap: 12px;
  padding: 8px 16px;
  background: var(--van-background-2, #fff);
  box-shadow: 0 -2px 8px rgb(0 0 0 / 8%);
}

.action-bar .van-button {
  flex: 1;
}
.booking-slot.ispast :deep(.van-grid-item__content) {
  background: var(--slot-bg, #f4f5f7);
}
</style>
