import type { ComputedRef, Ref } from 'vue'
export interface SlotTime {
  date: number
  id: number
}

const pad = (n: number) => String(n).padStart(2, '0')
const fmt = (d: Date) => `${pad(d.getHours())}:${pad(d.getMinutes())}`

export function useSlotTime(
  weekDays: ComputedRef<Date[]> | Ref<Date[]>,
  bookingSlots: Ref<number[][]> | Ref<number[]>,
  cancelingSlots?: Ref<number[][]> | Ref<number[]>,
) {
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

  /**
   * 该槽位是否已过期（含当天已过去的槽位）。
   */
  function isPastBlock(slottime: SlotTime): boolean {
    const day = weekDays.value.at(slottime.date)
    if (!day) return true
    const end = new Date(day)
    const time = timesDate.at(slottime.id)
    if (!time) return true
    end.setHours(time.getHours(), time.getMinutes(), 0, 0)
    return end.getTime() <= Date.now()
  }

  function isSelected(slottime: SlotTime): boolean {
    const canceling = cancelingSlots?.value ?? []
    if (bookingSlots.value.length === 0 && canceling.length === 0) return false
    return includesSlot(slottime, bookingSlots.value) || includesSlot(slottime, canceling)
  }

  function includesSlot(slottime: SlotTime, slots: number[][] | number[]) {
    if (slots.length === 0) return false
    // 形态 1：按天分组（桌面端 `number[][]`），首项必为数组
    if (Array.isArray(slots[0])) {
      return (slots[slottime.date] as number[] | undefined)?.includes(slottime.id) ?? false
    }
    // 形态 2：扁平数组（移动端 `number[]`）
    return (slots as number[]).includes(slottime.id)
  }

  let timesDate: Date[] = []

  function makeTimeLabels(totalSlots: number): string[] {
    timesDate = []
    let start = new Date()
    start.setHours(8, 0, 0, 0)
    const allminis = 960
    const step = allminis / totalSlots
    let current = new Date(start)
    const times: string[] = []

    for (let i = 0; i < totalSlots; i++) {
      timesDate.push(current)
      const next = new Date(current)
      next.setMinutes(next.getMinutes() + step)
      times.push(`${fmt(current)}-${fmt(next)}`)
      current = next
    }
    return times
  }

  return { isPastDay, isToday, isPastBlock, isSelected, makeTimeLabels }
}
