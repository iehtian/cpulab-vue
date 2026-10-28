<template>
  <div class="device-reservation">
    <el-card>
      <div style="display: flex; justify-content: space-between; align-items: center">
        <el-date-picker
          v-model="monday"
          type="week"
          format="[Week] ww"
          placeholder="请选择周"
        />
        <el-button-group class="mb-4">
          <el-button
            type="primary"
            :icon="ArrowLeft"
            @click="changeWeek(-7)"
            >Previous</el-button
          >
          <el-button
            type="primary"
            @click="resetWeek"
            >This</el-button
          >
          <el-button
            type="primary"
            @click="changeWeek(7)"
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
              // is_ordered: isBooked(slottime),
            },
          ]"
          :style="{ 'background-color': bookedSlots[slottime.date]?.[slottime.id]?.color }"
          @click="toggleSelect(slottime)"
        >
          <div class="slot-time">{{ bookedSlots[slottime.date]?.[slottime.id]?.user_name }}</div>
        </div>
      </div>
    </div>
    <Transition>
      <ReservationConfirm
        v-if="selectedSlots.length"
        :selected-slot="selectedSlots"
        @confirm="submit"
      ></ReservationConfirm>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import ReservationConfirm from '@/components/ReservationConfirm.vue'
import { changeDate, dateStr, getMonday, timeLabels, weekdayLabels } from '@/utils/date'
import { getBookings, submitBookings } from '@/api/booking'
import type { BookingInfo } from '@/api/booking'
import { useSlotTime } from '@/composables/useSlotTime'
import type { SlotTime } from '@/composables/useSlotTime'
import { useUserStore } from '@/stores/user'
import 'dayjs/locale/zh-cn'

const userStore = useUserStore()

const monday = ref(getMonday(new Date()))
const selectedSlots = ref<number[][]>([])
const bookedSlots = ref<Record<number, BookingInfo>[]>([])

const weekDays = computed(() => {
  const days: Date[] = []
  const current = new Date(monday.value)
  for (let i = 0; i < 7; i++) {
    days.push(new Date(current))
    current.setDate(current.getDate() + 1)
  }
  return days
})

const slotTimes = computed(() => {
  const times: SlotTime[] = []
  for (let i = 0; i < 32; i++) {
    for (let j = 0; j < 7; j++) {
      times.push({ date: j, id: i })
    }
  }
  return times
})

const { isPastBlock, isSelected } = useSlotTime(weekDays, selectedSlots)

function changeWeek(offset: number) {
  monday.value = changeDate(monday.value, offset)
  selectedSlots.value = []
}

function resetWeek() {
  // monday.value = new Date()
  // selectedSlots.value = []
}

function toggleSelect(slottime: SlotTime) {
  if (isPastBlock(slottime)) {
    return
  }
  if (!userStore.loggedIn) {
    return
  }

  const daySlots = (selectedSlots.value[slottime.date] ??= [])
  const index = daySlots.indexOf(slottime.id)
  if (index > -1) {
    daySlots.splice(index, 1)
  } else {
    daySlots.push(slottime.id)
  }
}

const submit = () => {
  for (let i = 0; i < 7; i++) {
    const slots = (selectedSlots.value[i] ??= [])
    if (slots.length) {
      const date = weekDays.value[i]!
      submitBookings('a', { date, slots })
    }
  }
}

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

function dedupeUserNames(bookings: Record<number, BookingInfo>[]) {
  for (const date of bookings) {
    let lastUserName = ''
    for (const [, value] of Object.entries(date)) {
      if (value.user_name !== lastUserName) {
        lastUserName = value.user_name
      } else {
        value.user_name = ''
      }
    }
  }
}

function fetchBookings() {
  const requests = weekDays.value.map((day) => getBookings('a', dateStr(day)))
  Promise.all(requests).then((res) => {
    const sorted = sortBookings(res)
    dedupeUserNames(sorted)
    bookedSlots.value = sorted
  })
}

function isBooked(slottime: SlotTime) {
  return Object.hasOwn(bookedSlots.value.at(slottime.date) ?? {}, slottime.id)
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
