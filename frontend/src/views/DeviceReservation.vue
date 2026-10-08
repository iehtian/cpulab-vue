<template>
  <div class="device-reservation">
    <el-card>
      <div style="display: flex; justify-content: space-between; align-items: center">
        <el-date-picker
          v-model="Monday"
          type="week"
          format="YYYY-MM-DD"
          placeholder="请选择周"
        />
        <el-button-group class="mb-4">
          <el-button
            type="primary"
            :icon="ArrowLeft"
            @click="prevWeek"
            >Previous</el-button
          >
          <el-button
            type="primary"
            @click="resetWeek"
            >This</el-button
          >
          <el-button
            type="primary"
            @click="nextWeek"
          >
            Next<el-icon class="el-icon--right">
              <ArrowRight />
            </el-icon>
          </el-button>
        </el-button-group>
      </div>
    </el-card>
    <div class="grid-scroll">
      <div class="week-grid">
        <!-- 表头：左上角 + 7 天 -->
        <div class="grid-cell grid-corner week-header"></div>
        <div
          v-for="(d, i) in 7"
          :key="`d-${i}`"
          class="grid-cell grid-day week-header"
        >
          <div class="day-wd">{{ weekdayLabels[i] }}</div>
          <div class="day-date">{{ dateStr(weekDays[i]!) }}</div>
        </div>

        <div
          v-for="(label, i) in timeLabels"
          :key="`h-${i}`"
          class="grid-cell grid-hour"
          :style="{ gridRow: i + 2 }"
        >
          <div class="slot-time">{{ label }}</div>
        </div>

        <div
          v-for="slottime in slotTimes"
          :key="`d-${slottime.date}-${slottime.id}`"
          class="grid-cell grid-corner booking-slot"
          :class="[
            {
              ispast: isPastBlock(slottime),
              selected: isSelected(slottime),
              // is_ordered: is_order(slottime),
            },
          ]"
          :style="{ 'background-color': ordered[slottime.date]?.[slottime.id]?.color }"
          @click="toggleSelect(slottime)"
        >
          <div class="slot-time">{{ ordered[slottime.date]?.[slottime.id]?.user_name }}</div>
        </div>
      </div>
    </div>
    <div>order: {{ ordered }}</div>
    <Transition>
      <confirmbuton
        v-if="selectedSlot.length"
        :selectedSlot="selectedSlot"
        @confirm="sbumit()"
      ></confirmbuton>
    </Transition>
  </div>
</template>

<script setup lang="ts">
interface slotTime {
  date: number
  id: number
}

import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { computed, ref, watch } from 'vue'
import confirmbuton from '@/components/ReservationConfirm.vue'
const today = ref(new Date())
const Monday = ref(new Date())
const d = new Date(today.value) // 复制而非用数字构造
d.setDate(d.getDate() - ((d.getDay() + 6) % 7))
Monday.value = d

const selectedSlot = ref<number[][]>([])

function prevWeek() {
  const next = new Date(Monday.value)
  next.setDate(next.getDate() - 7)
  Monday.value = next // 整体替换
  selectedSlot.value = []
}

function nextWeek() {
  const next = new Date(Monday.value)
  next.setDate(next.getDate() + 7)
  Monday.value = next // 整体替换
  selectedSlot.value = []
}

function resetWeek() {
  // Monday.value = new Date()
  // selectedSlot.value = []
}

const weekDays = computed(() => {
  const tmp = new Date(Monday.value)
  console.log(tmp)
  const weekdays: Date[] = []
  for (let i = 0; i < 7; i++) {
    weekdays.push(new Date(tmp))
    tmp.setDate(tmp.getDate() + 1)
  }
  console.log(weekdays)
  return weekdays
})

// 不依赖响应式数据，模块加载时计算一次即可
const timeLabels: string[] = (() => {
  const times: string[] = []
  const start = { Hour: 8, Minute: '00' }
  const end = { Hour: 8, Minute: '00' }
  for (let i = 0; i < 32; i++) {
    const hour = (i % 2) + 8 + Math.floor(i / 2)
    const minute = i % 2 === 0 ? '30' : '00'
    start.Hour = end.Hour
    start.Minute = end.Minute
    end.Hour = hour
    end.Minute = minute
    times.push(`${start.Hour}: ${start.Minute} - ${end.Hour}: ${end.Minute}`)
  }
  return times
})()

function dateStr(d: Date): string {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

const slotTimes = computed(() => {
  const times: slotTime[] = []
  for (let i = 0; i < 32; i++) {
    for (let j = 0; j < 7; j++) {
      times.push({ date: j, id: i })
    }
  }
  return times
})

function isPastDay(d: number): boolean {
  const t = new Date()
  t.setHours(0, 0, 0, 0)
  const dd = new Date(weekDays.value.at(d)!)
  dd.setHours(0, 0, 0, 0)
  return dd.getTime() < t.getTime()
}

function isToday(d: Date): boolean {
  const t = new Date()
  return (
    d.getDate() === t.getDate() &&
    d.getMonth() === t.getMonth() &&
    d.getFullYear() === t.getFullYear()
  )
}

function isSelected(slottime: slotTime): boolean {
  return selectedSlot.value.at(slottime.date)?.includes(slottime.id) ?? false
}

function isPastBlock(slottime: slotTime): boolean {
  const end = new Date(weekDays.value.at(slottime.date)!)
  const slot = slottime.id + 1
  end.setHours(8 + Math.floor(slot / 2), slot % 2 === 0 ? 0 : 30, 0, 0)
  return end.getTime() <= Date.now() || isPastDay(slottime.date)
}

const weekdayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

function toggleSelect(slottime: slotTime) {
  if (isPastBlock(slottime)) {
    return
  }
  const arr = (selectedSlot.value[slottime.date] ??= [])
  console.log(arr)
  const idx = arr.indexOf(slottime.id)
  console.log(idx)
  if (idx > -1) {
    arr.splice(idx, 1)
  } else {
    arr.push(slottime.id)
  }
}
import 'dayjs/locale/zh-cn'
import { submitBookings, getBookings } from '@/api/booking'
import type { BookingInfo } from '@/api/booking'
const sbumit = () => {
  for (let i = 0; i < 7; i++) {
    const slots = (selectedSlot.value[i] ??= [])
    if (slots.length) {
      const date = weekDays.value[i]!
      console.log({ date, slots })
      submitBookings('a', { date, slots })
    }
  }
}

const ordered = ref<Record<number, BookingInfo>[]>([])

function sortBookings(bookings: Record<number, BookingInfo>[]): Record<number, BookingInfo>[] {
  const res: Record<number, BookingInfo>[] = []
  for (const date of bookings) {
    const sortedObj = Object.fromEntries(
      Object.entries(date).sort(([a], [b]) => a.localeCompare(b)),
    )
    res.push(sortedObj)
  }
  return res
}

function duplicateremoval(bookings: Record<number, BookingInfo>[]) {
  for (const date of bookings) {
    let user_nameSet = ''
    for (const [_, value] of Object.entries(date)) {
      if (value.user_name !== user_nameSet) {
        user_nameSet = value.user_name
      } else {
        value.user_name = ''
      }
    }
  }
}

function fetchBookings() {
  const pormise_week = []
  for (const days of weekDays.value) {
    pormise_week.push(getBookings('a', dateStr(days)))
  }
  Promise.all(pormise_week).then((res) => {
    console.log(res)
    const sortedRes = sortBookings(res)
    duplicateremoval(sortedRes)
    ordered.value = sortedRes
  })
}

function is_order(slottime: slotTime) {
  return Object.hasOwn(ordered.value.at(slottime.date) ?? {}, slottime.id)
}

watch(weekDays, fetchBookings, { immediate: true })
</script>

<style scoped>
.week-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  grid-template-rows: 48px repeat(32, 1fr);
  border-left: var(--el-border);
  border-top: var(--el-border);
}

.grid-cell {
  border-right: var(--el-border);
  border-bottom: var(--el-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.grid-scroll {
  max-height: 70vh;
  overflow-y: auto;
  /* 内容超出就在框架内滚 */
  border: var(--el-border);
  border-radius: 4px;
}

.week-header {
  position: sticky;
  top: 0;
  background: var(--el-bg-color);
}

.booking-slot {
  background: #effaf3;
  height: 26px;
}

.el-aside {
  background-color: #d3dce6;
}

.el-main {
  background-color: #e9eef3;
}

.ispast {
  background: #cbd5e0;
}

.selected {
  background: var(--el-color-primary);
  border: 1px solid var(--el-color-primary);
}

.is_ordered {
  background: #f56c6c !important;
}

.grid-hour {
  background: #eaf2ff;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
