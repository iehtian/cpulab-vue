function changeDate(oldDate: Date, offset: number): Date {
  const newDate = new Date(oldDate)
  newDate.setDate(newDate.getDate() + offset)
  return newDate
}

function dateStr(d: Date): string {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

function getMonday(date: Date): Date {
  const d = new Date(date)
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7))
  return d
}

const weekdayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

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
    times.push(`${start.Hour}:${start.Minute}-${end.Hour}:${end.Minute}`)
  }
  return times
})()

export { changeDate, dateStr, getMonday, timeLabels, weekdayLabels }
