import service from '@/utils/request'

export async function getDutyLog(instrumentId: string, weekStart: string) {
  const response = await service.get(`/api/duty_log/get_duty`, {
    params: {
      instrument_id: instrumentId,
      week_start: weekStart,
    },
  })
  return response.data || []
}

export type roster = {
  userName: string
  joinDate: string
  lastServed: string
}

export async function getDutyRoster(instrumentId: string, weekStart: string): Promise<roster[]> {
  const response = await service.get(`/api/duty_log/get_duty_roster`, {
    params: {
      instrument_id: instrumentId,
      week_start: weekStart,
    },
  })
  return response.data || []
}
