<script setup lang="ts">
  import { computed, ref, reactive } from 'vue'
  import { ElMessage } from 'element-plus'
  import {
    Clock,
    Monitor,
    Location,
    Check,
    Close,
    ArrowLeft,
    ArrowRight,
  } from '@element-plus/icons-vue'

  // 设备信息（实际场景由接口获取，这里简单 mock）
  const device = reactive({
    id: 'DEV-2026-001',
    name: '高性能计算节点 A1',
    location: '机房 3F-08',
    status: 'idle', // idle | busy | offline
  })

  type DeviceStatus = 'idle' | 'busy' | 'offline'
  const statusMap: Record<DeviceStatus, { text: string; type: 'success' | 'warning' | 'info' }> = {
    idle: { text: '空闲', type: 'success' },
    busy: { text: '占用', type: 'warning' },
    offline: { text: '离线', type: 'info' },
  }
  const currentStatus = computed(() => statusMap[device.status as DeviceStatus])

  // 时段配置：08:00 - 22:00，每小时一格，共 14 段
  const HOUR_START = 8
  const HOUR_END = 22
  const hours = Array.from({ length: HOUR_END - HOUR_START }, (_, i) => i + HOUR_START)

  // ---- 周视图 ----
  // 周起始（周一）
  function getMonday(d: Date): Date {
    const date = new Date(d)
    const day = date.getDay() // 0=周日 .. 6=周六
    const diff = day === 0 ? -6 : 1 - day
    date.setDate(date.getDate() + diff)
    date.setHours(0, 0, 0, 0)
    return date
  }
  const weekStart = ref(getMonday(new Date()))

  const weekdayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

  const weekDays = computed(() => {
    const arr: Date[] = []
    for (let i = 0; i < 7; i++) {
      const d = new Date(weekStart.value)
      d.setDate(d.getDate() + i)
      arr.push(d)
    }
    return arr
  })

  function fmtDate(d: Date): string {
    return `${d.getMonth() + 1}/${d.getDate()}`
  }

  function dateStr(d: Date): string {
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${d.getFullYear()}-${m}-${day}`
  }

  function isToday(d: Date): boolean {
    const t = new Date()
    return (
      d.getDate() === t.getDate() &&
      d.getMonth() === t.getMonth() &&
      d.getFullYear() === t.getFullYear()
    )
  }

  // 整天是否已过去（早于今天）
  function isPastDay(d: Date): boolean {
    const t = new Date()
    t.setHours(0, 0, 0, 0)
    const dd = new Date(d)
    dd.setHours(0, 0, 0, 0)
    return dd.getTime() < t.getTime()
  }

  function prevWeek() {
    const d = new Date(weekStart.value)
    d.setDate(d.getDate() - 7)
    weekStart.value = d
  }
  function nextWeek() {
    const d = new Date(weekStart.value)
    d.setDate(d.getDate() + 7)
    weekStart.value = d
  }
  function thisWeek() {
    weekStart.value = getMonday(new Date())
  }

  const weekRangeLabel = computed(() => {
    const a = weekDays.value[0]!
    const b = weekDays.value[6]!
    return `${fmtDate(a)} - ${fmtDate(b)}，${a.getFullYear()}`
  })

  // ---- 时段数据（7 天 × 14 段，mock）----
  type SlotStatus = 'available' | 'booked' | 'mine'
  interface CellSlot {
    dayOffset: number
    hour: number
    status: SlotStatus
    bookedBy?: string
  }

  const weekSlots = computed<CellSlot[][]>(() => {
    const seed = Math.floor(weekStart.value.getTime() / 86400000)
    const users = ['张三', '李四', '王五']
    const result: CellSlot[][] = []
    for (let d = 0; d < 7; d++) {
      const col: CellSlot[] = []
      for (const h of hours) {
        const hash = (seed + d * 13 + h * 7) % 10
        let status: SlotStatus = 'available'
        let bookedBy: string | undefined
        if (hash < 3) {
          status = 'booked'
          bookedBy = users[(d + h) % users.length]
        } else if (hash === 7) {
          status = 'mine'
          bookedBy = '我'
        }
        col.push({ dayOffset: d, hour: h, status, bookedBy })
      }
      result.push(col)
    }
    return result
  })

  // 合并连续同人段为一个 block（available 不合并，保持每段独立可选）
  interface Block {
    dayOffset: number
    hourStart: number
    rowSpan: number
    status: SlotStatus
    bookedBy?: string
  }

  const weekBlocks = computed<Block[][]>(() => {
    return weekSlots.value.map((col, d) => {
      const blocks: Block[] = []
      let i = 0
      while (i < col.length) {
        const cur = col[i]!
        let span = 1
        if (cur.status !== 'available') {
          while (i + span < col.length) {
            const nxt = col[i + span]!
            if (nxt.status !== cur.status || nxt.bookedBy !== cur.bookedBy) break
            span++
          }
        }
        blocks.push({
          dayOffset: d,
          hourStart: cur.hour,
          rowSpan: span,
          status: cur.status,
          bookedBy: cur.bookedBy,
        })
        i += span
      }
      return blocks
    })
  })

  const allBlocks = computed<Block[]>(() => weekBlocks.value.flat())

  // ---- 选中 ----
  const selected = ref<string[]>([]) // key = `${dateStr}|${start}-${end}`
  function slotKey(dayOffset: number, hourStart: number): string {
    const d = weekDays.value[dayOffset]!
    const s = String(hourStart).padStart(2, '0')
    const e = String(hourStart + 1).padStart(2, '0')
    return `${dateStr(d)}|${s}:00-${e}:00`
  }

  function isPastBlock(block: Block): boolean {
    return isPastDay(weekDays.value[block.dayOffset]!)
  }

  function toggleSelect(block: Block) {
    if (block.status !== 'available' || isPastBlock(block)) return
    const k = slotKey(block.dayOffset, block.hourStart)
    const i = selected.value.indexOf(k)
    if (i >= 0) selected.value.splice(i, 1)
    else selected.value.push(k)
  }

  function isSelected(block: Block): boolean {
    return block.status === 'available' && selected.value.includes(slotKey(block.dayOffset, block.hourStart))
  }

  // ---- 我的预约 ----
  interface Booking {
    id: string
    date: string
    range: string
    createdAt: string
  }

  const myBookings = ref<Booking[]>([
    { id: 'B001', date: dateStr(new Date()), range: '15:00-16:00', createdAt: '2026-09-01 09:12' },
  ])

  const submitting = ref(false)
  function submit() {
    if (selected.value.length === 0) {
      ElMessage.warning('请至少选择一个时段')
      return
    }
    submitting.value = true
    setTimeout(() => {
      selected.value.forEach((k) => {
        const parts = k.split('|')
        const date = parts[0] ?? ''
        const range = parts[1] ?? ''
        myBookings.value.unshift({
          id: 'B' + Math.random().toString(36).slice(2, 7).toUpperCase(),
          date,
          range,
          createdAt: new Date().toLocaleString('zh-CN'),
        })
      })
      selected.value = []
      ElMessage.success('预约成功')
      submitting.value = false
    }, 600)
  }

  function cancelBooking(id: string) {
    const i = myBookings.value.findIndex((b) => b.id === id)
    if (i >= 0) {
      myBookings.value.splice(i, 1)
      ElMessage.success('已取消预约')
    }
  }

  const totalHours = computed(() => selected.value.length)

  // ---- 网格定位 ----
  function gridColumn(d: number): number {
    return d + 2 // 第 1 列是时段标签，2~8 是 7 天
  }
  function gridRow(hour: number): number {
    return hour - HOUR_START + 2 // 第 1 行是表头，2~15 是 14 段
  }
</script>

<template>
  <div class="reservation-page">
    <!-- 设备信息卡片 -->
    <el-card shadow="never" class="device-card">
      <div class="device-head">
        <div class="device-title">
          <el-icon class="device-icon">
            <Monitor />
          </el-icon>
          <span>{{ device.name }}</span>
          <el-tag size="small" :type="currentStatus.type" effect="light">
            {{ currentStatus.text }}
          </el-tag>
        </div>
        <div class="device-meta">
          <span><el-icon>
              <Location />
            </el-icon>{{ device.location }}</span>
          <span><el-icon>
              <Monitor />
            </el-icon>{{ device.id }}</span>
        </div>
      </div>
    </el-card>

    <!-- 周历预约主区 -->
    <el-card shadow="never" class="booking-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon>
              <Clock />
            </el-icon>
            <span>预约时段</span>
            <el-tag type="info" effect="plain" size="small">{{ weekRangeLabel }}</el-tag>
          </div>
          <div class="header-right">
            <el-button-group>
              <el-button :icon="ArrowLeft" size="small" @click="prevWeek">上一周</el-button>
              <el-button size="small" @click="thisWeek">本周</el-button>
              <el-button size="small" @click="nextWeek">
                下一周<el-icon class="el-icon--right">
                  <ArrowRight />
                </el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <!-- 周历网格 -->
      <div class="week-grid">
        <!-- 表头：左上角 + 7 天 -->
        <div class="grid-cell grid-corner"></div>
        <div v-for="(d, i) in weekDays" :key="`d-${i}`" class="grid-cell grid-day" :class="{ 'is-today': isToday(d) }">
          <div class="day-wd">{{ weekdayLabels[i] }}</div>
          <div class="day-md">
            {{ fmtDate(d) }}<span v-if="isToday(d)" class="today-mark">今天</span>
          </div>
        </div>

        <!-- 左侧时段标签列 -->
        <div v-for="h in hours" :key="`h-${h}`" class="grid-cell grid-hour" :style="{ gridRow: gridRow(h) }">
          {{ String(h).padStart(2, '0') }}:00
        </div>

        <!-- 数据格 / 合并块 -->
        <div v-for="block in allBlocks" :key="`b-${block.dayOffset}-${block.hourStart}`" class="grid-cell cell" :class="[
          `cell--${block.status}`,
          {
            'cell--active': isSelected(block),
            'cell--past': isPastBlock(block),
          },
        ]" :style="{
            gridColumn: gridColumn(block.dayOffset),
            gridRow: `${gridRow(block.hourStart)} / span ${block.rowSpan}`,
          }" @click="toggleSelect(block)">
          <template v-if="block.status === 'available'">
            <el-icon v-if="isSelected(block)" class="check-icon">
              <Check />
            </el-icon>
            <span v-else class="cell-hint">可预约</span>
          </template>
          <span v-else-if="block.status === 'booked'" class="cell-name">
            <el-icon class="name-icon">
              <Close />
            </el-icon>{{ block.bookedBy }}
          </span>
          <span v-else class="cell-name cell-name--mine">我的预约</span>
        </div>
      </div>

      <!-- 图例 + 提交 -->
      <div class="legend">
        <span><i class="dot dot--available"></i>可预约</span>
        <span><i class="dot dot--booked"></i>已被占用</span>
        <span><i class="dot dot--mine"></i>我的预约</span>
        <span><i class="dot dot--past"></i>已过期</span>
      </div>

      <div class="submit-bar">
        <span class="summary">已选 <b>{{ totalHours }}</b> 个时段</span>
        <el-button type="primary" :loading="submitting" @click="submit">提交预约</el-button>
      </div>
    </el-card>

    <!-- 我的预约 -->
    <el-card shadow="never" class="mine-card">
      <template #header>我的预约</template>
      <el-table :data="myBookings" stripe size="large" empty-text="暂无预约">
        <el-table-column prop="id" label="预约号" width="120" />
        <el-table-column prop="date" label="日期" width="130" />
        <el-table-column prop="range" label="时段" width="160" />
        <el-table-column prop="createdAt" label="提交时间" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="cancelBooking(row.id)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
  .reservation-page {
    max-width: 1100px;
    margin: 24px auto;
    padding: 0 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  /* 设备卡片 */
  .device-head {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .device-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
  }

  .device-icon {
    color: var(--el-color-primary);
    font-size: 20px;
  }

  .device-meta {
    display: flex;
    gap: 24px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .device-meta span {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  /* 预约主区 */
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .header-left span {
    font-weight: 600;
  }

  /* 周历网格 */
  .week-grid {
    display: grid;
    grid-template-columns: 56px repeat(7, 1fr);
    grid-template-rows: 48px repeat(14, 52px);
    grid-auto-flow: dense;
    border-left: 1px solid var(--el-border);
    border-top: 1px solid var(--el-border);
    background: var(--el-bg-color);
    overflow: auto;
  }

  /* 通用网格单元：只画右、下边框，避免相邻重叠 */
  .grid-cell {
    border-right: 1px solid var(--el-border);
    border-bottom: 1px solid var(--el-border);
  }

  .grid-corner {
    grid-column: 1;
    grid-row: 1;
  }

  .grid-day {
    grid-row: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    background: var(--el-fill-color-light);
  }

  .grid-day.is-today {
    background: var(--el-color-primary-light-9);
  }

  .day-wd {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .day-md {
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .today-mark {
    font-size: 11px;
    color: var(--el-color-primary);
    font-weight: 400;
  }

  .grid-hour {
    grid-column: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    background: var(--el-fill-color-light);
  }

  /* 数据格 */
  .cell {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.18s;
    font-size: 12px;
    text-align: center;
    padding: 2px;
  }

  .cell--available {
    background: var(--el-bg-color);
  }

  .cell--available:hover {
    background: var(--el-color-primary-light-9);
  }

  .cell--active {
    background: var(--el-color-primary-light-9) !important;
    color: var(--el-color-primary);
    box-shadow: inset 0 0 0 2px var(--el-color-primary);
  }

  .check-icon {
    font-size: 16px;
  }

  .cell-hint {
    color: var(--el-text-color-placeholder);
  }

  .cell--booked {
    background: var(--el-fill-color-light);
    color: var(--el-text-color-secondary);
    cursor: not-allowed;
  }

  .cell--booked:hover {
    background: var(--el-fill-color-light);
  }

  .cell-name {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    line-height: 1.3;
  }

  .name-icon {
    font-size: 14px;
    opacity: 0.6;
  }

  .cell-name--mine {
    color: var(--el-color-success);
    font-weight: 600;
  }

  .cell--mine {
    background: var(--el-color-success-light-9);
    cursor: default;
  }

  .cell--mine:hover {
    background: var(--el-color-success-light-9);
  }

  .cell--past {
    background: var(--el-fill-color) !important;
    color: var(--el-text-color-disabled);
    cursor: not-allowed;
    position: relative;
  }

  .cell--past.cell--available {
    background: var(--el-fill-color) !important;
  }

  .cell--past:hover {
    background: var(--el-fill-color) !important;
  }

  /* 图例 */
  .legend {
    display: flex;
    gap: 20px;
    margin-top: 16px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
    flex-wrap: wrap;
  }

  .legend span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .dot {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    display: inline-block;
    border: 1px solid var(--el-border);
  }

  .dot--available {
    background: var(--el-bg-color);
  }

  .dot--booked {
    background: var(--el-fill-color-light);
  }

  .dot--mine {
    background: var(--el-color-success-light-9);
    border-color: var(--el-color-success);
  }

  .dot--past {
    background: var(--el-fill-color);
  }

  /* 提交栏 */
  .submit-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px dashed var(--el-border);
  }

  .summary {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }

  .summary b {
    color: var(--el-color-primary);
    font-size: 18px;
    margin: 0 4px;
  }
</style>
