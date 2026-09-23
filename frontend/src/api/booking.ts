import service from '@/utils/request'
async function getBookings(instrument, date) {
  try {
    const response = await service.get(`/api/bookings/${instrument}/${date}`)

    const data = response.data
    console.log('获取的预约数据:', data)

    return data.bookings || {}
  } catch (error) {
    console.error('获取已预约时间段时出错:', error)
  }
}

async function submitBookings(instrument, submitData) {
  const thisDate = submitData.date
  const slots = submitData.slots

  if (!thisDate || slots.length === 0) {
    alert('请先选择日期和时间段')
    return
  }

  try {
    const targetData = {
      instrument: instrument,
      date: thisDate,
      slots: slots,
    }

    console.log('发送的数据:', targetData)

    // 使用 axios.post，第二个参数直接传对象
    await service.post(`/api/info_save`, targetData)
  } catch (error) {
    return false
  }
}

async function cancelBookings(instrument, cancelData) {
  const thisDate = cancelData.date
  const slots = cancelData.slots

  if (!thisDate || slots.length === 0) {
    alert('请先选择日期和时间段')
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      alert('未登录，无法提交预约')
      return false
    }
    const targetData = {
      instrument: instrument,
      date: thisDate,
      slots: slots,
    }

    console.log('发送的数据:', targetData)
    await service.post(`/api/cancel_booking`, targetData)
  } catch (error) {
    return false
  }
}

export { getBookings, submitBookings, cancelBookings }
