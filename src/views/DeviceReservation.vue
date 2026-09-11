<template>
    <div class="device-reservation">
        <h1>Device Reservation</h1>
        <el-container>
            <el-aside width="200px">Aside</el-aside>
            <el-main>
                <el-card>
                    <div style="display: flex; justify-content: space-between; align-items: center">
                        <el-text>{{ weekRange }}</el-text>
                        <el-button-group class="mb-4">
                            <el-button type="primary" :icon="ArrowLeft" @click="prevWeek">Previous</el-button>
                            <el-button type="primary" @click="resetWeek">This</el-button>
                            <el-button type="primary" @click="nextWeek">
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
                        <div v-for="(d, i) in 7" :key="`d-${i}`" class="grid-cell grid-day week-header">
                            <div class="day-wd">{{ weekdayLabels[i] }}</div>
                            <div class="day-date">{{ weekDays[i] }}</div>
                        </div>

                        <div v-for="(label, i) in timeLabels" :key="`h-${i}`" class="grid-cell grid-hour"
                            :style="{ gridRow: i + 1 }">
                            <div class=" slot-time">{{ label }}</div>
                        </div>

                        <div v-for="slottime in slotTimes" :key="`d-${slottime.date}-${slottime.id}`"
                            class="grid-cell grid-corner booking-slot" :class="[{
                                'ispast': isPastBlock(slottime),
                                'selected': isSelected(slottime),
                            }
                            ]" @click="toggleSelect(slottime)">
                            <div class="slot-time">{{ slottime.id }}</div>
                        </div>

                    </div>
                </div>
            </el-main>
            <el-aside width="200px">Aside</el-aside>
        </el-container>

    </div>

</template>

<script setup lang="ts">
    interface slotTime {
        date: Date
        id: number
    }

    import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
    import { computed, ref } from 'vue'
    const thisdate = ref(new Date())
    const newdate = new Date(thisdate.value)
    newdate.setDate(newdate.getDate() - newdate.getDay() + 1)
    thisdate.value = newdate
    const selectedSlot = ref<string[]>([])

    function prevWeek() {
        const next = new Date(thisdate.value)
        next.setDate(next.getDate() - 7)
        thisdate.value = next  // 整体替换
        selectedSlot.value = []
    }

    function nextWeek() {
        const next = new Date(thisdate.value)
        next.setDate(next.getDate() + 7)
        thisdate.value = next  // 整体替换
        selectedSlot.value = []
    }

    function resetWeek() {
        thisdate.value = new Date()
        selectedSlot.value = []
    }

    const weekRange = computed(() => {
        const weekstart: string = dateStr(thisdate.value)
        const after = new Date(thisdate.value)
        after.setDate(after.getDate() + 7)
        const weekend: string = dateStr(after)
        return `${weekstart} - ${weekend}`
    })

    const weekDays = computed(() => {
        const tmp = new Date(thisdate.value)
        const weekdaysStr: string[] = []
        for (let i = 0; i < 7; i++) {
            weekdaysStr.push(dateStr(tmp))
            tmp.setDate(tmp.getDate() + 1)
        }
        return weekdaysStr
    })

    // 不依赖响应式数据，模块加载时计算一次即可
    const timeLabels: string[] = (() => {
        const times: string[] = []
        const start = { Hour: 8, Minute: '00' }
        const end = { Hour: 8, Minute: '00' }
        for (let i = 0; i < 32; i++) {
            const hour = i % 2 + 8 + Math.floor(i / 2)
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

    function slotTimeStr(slottime: slotTime): string {
        return `${dateStr(slottime.date)} ${slottime.id}`
    }


    const slotTimes = computed(() => {
        const tmp = new Date(thisdate.value)
        const times: slotTime[] = []
        const date: Date[] = []
        for (let i = 0; i < 7; i++) {
            const start = new Date(tmp)
            tmp.setDate(tmp.getDate() + 1)
            date.push(start)
        }

        for (let i = 0; i < 32; i++) {
            for (const d of date) {
                times.push({ date: d, id: i })
            }
        }

        return times
    })

    function isPastDay(d: Date): boolean {
        const t = new Date()
        t.setHours(0, 0, 0, 0)
        const dd = new Date(d)
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

    const weekdayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    function toggleSelect(slottime: slotTime) {
        if (selectedSlot.value.includes(slotTimeStr(slottime))) {
            console.log(selectedSlot.value)
            selectedSlot.value = selectedSlot.value.filter((s) => s !== slotTimeStr(slottime))
            console.log(selectedSlot.value)
            console.log("取消选择", slottime.id)
        } else {
            selectedSlot.value.push(slotTimeStr(slottime))
            console.log(selectedSlot.value)
        }
    }

</script>

<style>
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
        /* 或固定 px，比如 560px */
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
        background: var(--el-fill-color-light);
        height: 26px;
    }

    .el-aside {
        background-color: #d3dce6;
    }

    .el-main {
        background-color: #e9eef3;
    }

    .ispast {
        background: red;
    }

    .selected {
        background: var(--el-color-primary);
        border: 1px solid var(--el-color-primary);
    }
</style>