import { ref, watch } from 'vue'
import type { Ref } from 'vue'
import { showSuccessToast } from 'vant'
import { dateStr } from '@/utils/date'
import { getBookings, submitBookings, cancelBookings } from '@/api/booking'
import type { BookingInfo } from '@/api/booking'

export function useReservation(deviceId: Ref<string>, date: Ref<Date>) {
  const bookingSlots = ref<number[]>([])
  const cancelingSlots = ref<number[]>([])
  const dayBookings = ref<Record<number, BookingInfo>>({})

  async function fetchBookings() {
    dayBookings.value = await getBookings(deviceId.value, dateStr(date.value))
  }

  function clearSelection() {
    bookingSlots.value = []
    cancelingSlots.value = []
  }

  async function submit() {
    if (bookingSlots.value.length === 0) return
    const ok = await submitBookings(deviceId.value, {
      date: date.value,
      slots: bookingSlots.value,
    })
    if (ok === false) return
    showSuccessToast('预约成功')
    clearSelection()
    await fetchBookings()
  }

  async function cancel() {
    if (cancelingSlots.value.length === 0) return
    const ok = await cancelBookings(deviceId.value, {
      date: date.value,
      slots: cancelingSlots.value,
    })
    if (ok === false) return
    showSuccessToast('已取消预约')
    clearSelection()
    await fetchBookings()
  }

  watch(
    [deviceId, date],
    () => {
      clearSelection()
      fetchBookings()
    },
    { immediate: true },
  )

  return { bookingSlots, cancelingSlots, dayBookings, fetchBookings, submit, cancel }
}
