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
                            <div class="day-date">{{ weekdays[i] }}</div>
                        </div>
                        <div v-for="(d, i) in 8 * 32" :key="`d-${i}`" class="grid-cell grid-corner booking-slot">
                            <div v-if="slotTimesStr[i]" class="slot-time">{{ slotTimesStr[i] }}</div>
                            <div v-else class="slot-time">{{ d }}</div>
                        </div>

                    </div>
                </div>
            </el-main>
            <el-aside width="200px">Aside</el-aside>
        </el-container>

    </div>

</template>

<script setup lang="ts">
    import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
    import { computed, ref } from 'vue'
    const thisdata = ref(new Date())

    function prevWeek() {
        const next = new Date(thisdata.value)
        next.setDate(next.getDate() - 7)
        thisdata.value = next  // 整体替换
    }

    function nextWeek() {
        const next = new Date(thisdata.value)
        next.setDate(next.getDate() + 7)
        thisdata.value = next  // 整体替换
    }

    function resetWeek() {
        thisdata.value = new Date()
    }

    function getWeekRange(data: Date): string {
        const weekdata: number = data.getDay()
        const before = new Date(data)
        before.setDate(data.getDate() - weekdata)
        const weekstart: string = before.toLocaleDateString()
        const after = new Date(data)
        after.setDate(data.getDate() + 6 - weekdata)
        const weekend: string = after.toLocaleDateString()
        return `${weekstart} - ${weekend}`
    }

    function getWeekDays(data: Date): string[] {
        const weekdata: number = data.getDay()
        const before = new Date(data)
        before.setDate(data.getDate() - weekdata)
        const weekdays: Date[] = []
        for (let i = 0; i < 7; i++) {
            weekdays.push(new Date(before))
            before.setDate(before.getDate() + 1)
        }
        const weekdaysStr: string[] = []
        weekdays.forEach((d) => {
            const str = d.toLocaleDateString()
            weekdaysStr.push(str.slice(5, str.length))
        })
        return weekdaysStr
    }

    const weekRange = computed(() => {
        return getWeekRange(thisdata.value)
    })
    const weekdays = computed(() => {
        return getWeekDays(thisdata.value)
    })
    const slotTimesStr = computed(() => {
        const times: string[] = []
        const start = {
            Hour: 8,
            Minute: '00'
        }
        const end = {
            Hour: 8,
            Minute: '30'
        }
        for (let i = 0; i < 32; i++) {
            times.push(`${start.Hour}:${start.Minute} - ${end.Hour}:${end.Minute}`)
            const hour = i % 2 + 8 + Math.floor(i / 2)
            const minute = i % 2 === 0 ? '00' : '30'
            start.Hour = end.Hour
            start.Minute = end.Minute
            end.Hour = hour
            end.Minute = minute
            times.push('', '', '', '', '', '', '') // 剩余 7 列占位
        }
        return times
    })

    const weekdayLabels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']


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
</style>