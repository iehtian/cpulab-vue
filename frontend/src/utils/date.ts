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

export { changeDate, dateStr, getMonday, weekdayLabels }
