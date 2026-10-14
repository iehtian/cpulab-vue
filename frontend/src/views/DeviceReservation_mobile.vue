<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; align-items: center">
      <van-cell
        class="date-cell"
        :value="dateStr(date)"
        @click="show = true"
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
        v-model:show="show"
        :show-confirm="false"
        @confirm="onConfirm"
      />
    </div>
  </el-card>
  <div class="grid-scroll">
    <div class="day-grid">
      <div
        v-for="id of 32"
        :key="id"
        class="grid-cell grid-corner booking-slot"
        :class="[
          {
            ispast: isPastBlock({ date: 0, id: id - 1 }),
            selected: isSelected({ date: 0, id: id - 1 }),
            // is_ordered: is_order(id),
          },
        ]"
        @click="toggleSelect(id - 1)"
        :style="{ 'background-color': ordered?.[id - 1]?.color }"
      >
        <div class="slot-time">
          {{ ordered?.[id - 1]?.user_name ?? timeLabels.at(id - 1) }}
        </div>
      </div>
    </div>
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
import { changeDate, dateStr, timeLabels } from '@/utils/date.ts'
import { getBookings, submitBookings, cancelBookings } from '@/api/booking.ts'
import type { BookingInfo } from '@/api/booking'
import { useSlotTime } from '@/composables/useSlotTime'
const show = ref(false)
const date = ref(new Date())
const bookingSlots = ref<number[]>([]) // 待新预约
const cancelingSlots = ref<number[]>([]) // 待取消

const ordered = ref<Record<number, BookingInfo>>({})

const dateList = computed(() => [date.value])
const { isPastBlock, isSelected } = useSlotTime(dateList, bookingSlots, cancelingSlots)
import { useCheckStore } from '@/stores/user.ts'

const checkStore = useCheckStore()

function cancel_order(id: number) {
  const index = cancelingSlots.value.indexOf(id)
  if (index === -1) {
    cancelingSlots.value.push(id)
  } else {
    cancelingSlots.value.splice(index, 1)
  }
}

function submit_order(id: number) {
  const index = bookingSlots.value.indexOf(id)
  if (index === -1) {
    bookingSlots.value.push(id)
  } else {
    bookingSlots.value.splice(index, 1)
  }
}

function toggleSelect(id: number) {
  if (!checkStore.loggedIn || isPastBlock({ date: 0, id: id }) || is_order(id)) {
    return
  }
  if (is_cancel(id)) {
    cancel_order(id)
  } else {
    submit_order(id)
  }
}

function fetchBookings() {
  console.log(date.value)
  const pormise_day = getBookings('a', dateStr(date.value))
  pormise_day.then((res) => {
    ordered.value = res
    console.log(res)
  })
}
watch(date, fetchBookings, { immediate: true })
function is_order(id: number) {
  if (ordered.value.hasOwnProperty(id)) {
    return ordered.value[id]?.user_name !== checkStore.userName
  }
  return false
}

function is_cancel(id: number) {
  if (ordered.value.hasOwnProperty(id)) {
    return ordered.value[id]?.user_name === checkStore.userName
  }
  return false
}

const submit = () => {
  const pormise_day = submitBookings('a', {
    date: date.value,
    slots: bookingSlots.value,
  })
  pormise_day.then((res: any) => {
    // 刷新页面
    window.location.reload()
  })
}

const cancel = () => {
  const pormise_day = cancelBookings('a', {
    date: date.value,
    slots: cancelingSlots.value,
  })
  pormise_day.then((res: any) => {
    // 刷新页面
    window.location.reload()
  })
}

const onConfirm = (selectedDate: Date) => {
  date.value = selectedDate
  show.value = false
}

function changeSelectedDate(offset: number) {
  date.value = changeDate(date.value, offset)
  bookingSlots.value = []
  cancelingSlots.value = []
}
</script>

<style scoped>
:deep(.date-cell .van-cell__value) {
  text-align: center;
}
.day-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(8, 1fr);
  border-left: var(--el-border);
  border-top: var(--el-border);
  gap: 6px;
}
.booking-slot {
  background: #effaf3;
  /* height: 26px; */
}
.grid-cell {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
}

.selected {
  background: var(--el-color-primary);
  border: var(--el-color-primary);
}
.ispast {
  background: #cbd5e0;
}
</style>
