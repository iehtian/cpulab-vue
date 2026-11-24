import service from '@/utils/request'
import type { ReagentCategory } from '@/constants/reagent'

export interface Reagent {
  id: number
  zoneId: number
  name: string
  casNumber: string
  category: ReagentCategory
  capacity: number | null
  bottleCount: number | null
  need2restock: boolean | null
  lastRemainder: number | null
}
export type ReagentPayload = Omit<
  Reagent,
  'id' | 'need2restock' | 'lastRemainder'
>
export type ReagentTimes = Reagent & {
  times: number
}

export async function getReagentsByZone(zoneId: number): Promise<Reagent[]> {
  const response = await service.get(`/api/reagent/all/${zoneId}`)
  return response.data.reagents || []
}

export async function upsertReagent(payload: ReagentPayload, userId: number): Promise<void> {
  await service.post('/api/reagent/upsert', {
    zone_id: payload.zoneId,
    user_id: userId,
    name: payload.name,
    CAS_number: payload.casNumber,
    category: payload.category,
    capacity: payload.capacity,
    bottle_count: payload.bottleCount,
  })
}

export async function deleteReagentById(id: number): Promise<void> {
  await service.delete(`/api/reagent/delete/${id}`)
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

export async function getAllReagents(): Promise<Reagent[]> {
  const response = await service.get('/api/reagent/all')
  return response.data.reagents || []
}
