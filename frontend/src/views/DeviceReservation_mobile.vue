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
        v-for="slottime of 32"
        class="grid-cell grid-corner booking-slot"
        :class="[
          {
            // ispast: isPastBlock(slottime),
            selected: isSelected(slottime),
            // is_ordered: is_order(slottime),
          },
        ]"
        @click="toggleSelect(slottime)"
        :style="{ 'background-color': ordered?.[slottime]?.color }"
      >
        <div class="slot-time">{{ ordered?.[slottime]?.user_name ?? timeLabels.at(slottime - 1) }}</div>
      </div>
    </div>
  </div>
  <van-button type="primary" v-if="selectedSlot.length > 0" @click="submit">提交预约</van-button>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { changeDate, dateStr,timeLabels } from '@/utils/date.ts'
import { getBookings,submitBookings } from '@/api/booking.ts'
import type { BookingInfo } from '@/api/booking'
const show = ref(false)
const date = ref(new Date())
const selectedSlot = ref<number[]>([])
const ordered = ref<Record<number, BookingInfo>>({})

function toggleSelect(slottime: number) {
  const index = selectedSlot.value.indexOf(slottime)
  if (index === -1) {
    selectedSlot.value.push(slottime)
  } else {
    selectedSlot.value.splice(index, 1)
  }
}

function fetchBookings() {
  console.log(date.value)
  const pormise_day =getBookings('a', dateStr(date.value))
  pormise_day.then((res)=>{
    ordered.value = res
    console.log(res)
  })
}
watch(date,fetchBookings,{immediate: true})

const  submit =() => {
  const pormise_day =submitBookings('a', {date:date.value, slots:selectedSlot.value})
  pormise_day.then((res: any)=>{
    // 刷新页面
    fetchBookings()

  })
}

const onConfirm = (selectedDate: Date) => {
  date.value = selectedDate
  show.value = false
}

function isSelected(slottime: number) {
  return selectedSlot.value.includes(slottime)
}

function changeSelectedDate(offset: number) {
  date.value = changeDate(date.value, offset)
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
  border:  var(--el-color-primary);
}
</style>
