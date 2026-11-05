import service from '@/utils/request'

export interface Reagent {
  id: number
  zoneId: number
  name: string
  casNumber: string
  category: number
  capacity: number | null
  bottleCount: number | null
  specification: string
  openDate: string | null
  need2restock: boolean | null
  usageLength: number | null
  lastUserName: string | null
  lastRemainder: number | null
}
export type ReagentPayload = Omit<
  Reagent,
  'id' | 'openDate' | 'need2restock' | 'usageLength' | 'lastUserName' | 'lastRemainder'
>
export type ReagentTimes = Reagent & {
  times: number
}

export async function getReagentsByZone(zoneId: number): Promise<Reagent[]> {
  const response = await service.get(`/api/reagent/all/${zoneId}`)
  return response.data.reagents || []
}

export async function upsertReagent(payload: ReagentPayload): Promise<void> {
  await service.post('/api/reagent/upsert', {
    zone_id: payload.zoneId,
    name: payload.name,
    CAS_number: payload.casNumber,
    category: payload.category,
    capacity: payload.capacity,
    bottle_count: payload.bottleCount,
    specification: payload.specification,
  })
}

export async function deleteReagentById(id: number): Promise<void> {
  await service.delete(`/api/reagent/delete/${id}`)
}

export async function openReagentById(id: number, openDate: string, userId: number): Promise<void> {
  await service.post('/api/reagent/open', { id, open_date: openDate, user_id: userId })
}

export async function markReagentNeed2Restock(id: number, need2restock: boolean): Promise<void> {
  await service.post('/api/reagent/mark_need2restock', { id, need2restock })
}

export async function getNeed2RestockReagents(): Promise<Reagent[]> {
  const response = await service.get('/api/reagent/get_need2restock_reagents')
  return response.data.reagents || []
}

export async function getCommonUsedReagents(userId: number): Promise<ReagentTimes[]> {
  const response = await service.get(`/api/reagent/get_common_used_reagents/${userId}`)
  return response.data.reagents || []
}
