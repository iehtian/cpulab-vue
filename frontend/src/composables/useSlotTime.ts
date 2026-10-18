import type { ComputedRef, Ref } from 'vue'

/**
 * 预约槽位（一个时间格）的统一表示。
 * - date: 该格所属日期在 `weekDays` 中的下标
 * - id:   一天 32 个半小时槽位的下标（0..31）
 */
export interface SlotTime {
  date: number
  id: number
}

/**
 * 一天 32 个半小时槽位对应的时间起点：
 * - id=0   -> 08:00 (结束 08:30)
 * - id=1   -> 08:30 (结束 09:00)
 * - ...
 * 与 utils/date.ts 中 timeLabels 的定义保持一致。
 */
function slotEndHour(id: number): number {
  return 8 + Math.floor((id + 1) / 2)
}

function slotEndMinute(id: number): number {
  return (id + 1) % 2 === 0 ? 0 : 30
}

export function useSlotTime(
  weekDays: ComputedRef<Date[]> | Ref<Date[]>,
  bookingSlots: Ref<number[][]> | Ref<number[]>,
  cancelingSlots: Ref<number[][]> | Ref<number[]>,
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
    const id = slottime.id - 1
    const day = weekDays.value.at(slottime.date)
    if (!day) return true
    const end = new Date(day)
    end.setHours(slotEndHour(id), slotEndMinute(id), 0, 0)
    return end.getTime() <= Date.now()
  }

  function isSelected(slottime: SlotTime): boolean {
    if (bookingSlots.value.length === 0 && cancelingSlots.value.length === 0) return false
    return isin(slottime, bookingSlots.value) || isin(slottime, cancelingSlots.value)
  }

  function isin(slottime: SlotTime, slots: number[][] | number[]) {
    if (slots.length === 0) return false
    // 形态 1：按天分组（桌面端 `number[][]`），首项必为数组
    if (Array.isArray(slots[0])) {
      return (slots[slottime.date] as number[] | undefined)?.includes(slottime.id) ?? false
    }
    // 形态 2：扁平数组（移动端 `number[]`）
    const res = (slots as number[]).includes(slottime.id)

    return res
  }

  return { isPastDay, isToday, isPastBlock, isSelected }
}
