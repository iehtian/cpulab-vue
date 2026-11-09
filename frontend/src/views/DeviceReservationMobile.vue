<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; align-items: center">
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
      <van-calendar
        v-model:show="showCalendar"
        :show-confirm="false"
        @confirm="onDateConfirm"
      />
    </div>
  </el-card>
  <div class="grid-scroll">
    <van-grid
      :column-num="4"
      clickable
    >
      <van-grid-item
        v-for="id of 32"
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
  </div>
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
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { changeDate, dateStr, timeLabels } from '@/utils/date'
import { getBookings, submitBookings, cancelBookings } from '@/api/booking'
import type { BookingInfo } from '@/api/booking'
import { useSlotTime } from '@/composables/useSlotTime'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const date = ref(new Date())
const showCalendar = ref(false)
const bookingSlots = ref<number[]>([]) // 待新预约
const cancelingSlots = ref<number[]>([]) // 待取消
const dayBookings = ref<Record<number, BookingInfo>>({})

const dateList = computed(() => [date.value])
const { isPastBlock, isSelected } = useSlotTime(dateList, bookingSlots, cancelingSlots)

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

async function fetchBookings() {
  dayBookings.value = await getBookings('a', dateStr(date.value))
}

const submit = async () => {
  await submitBookings('a', {
    date: date.value,
    slots: bookingSlots.value,
  })
  // 刷新页面
  window.location.reload()
}

const cancel = async () => {
  await cancelBookings('a', {
    date: date.value,
    slots: cancelingSlots.value,
  })
  // 刷新页面
  window.location.reload()
}

const onDateConfirm = (selectedDate: Date) => {
  date.value = selectedDate
  showCalendar.value = false
}

function changeSelectedDate(offset: number) {
  date.value = changeDate(date.value, offset)
  bookingSlots.value = []
  cancelingSlots.value = []
}

watch(date, fetchBookings, { immediate: true })
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

.booking-slot.ispast :deep(.van-grid-item__content) {
  background: #cbd5e0;
}

.slot-time {
  font-size: 12px;
}
</style>
