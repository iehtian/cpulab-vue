import service from '@/utils/request'

export interface Reagent {
  id: number
  zone_id: number
  name: string
  CAS_number: string | null
  category: number
  capacity: number | null
  bottle_count: number | null
  specification: string | null
  open_date: string | null
  expiry_date: string | null
}

export interface ReagentPayload {
  zoneId: number
  name: string
  casNumber: string | null
  category: number
  capacity: number | null
  bottleCount: number | null
  specification: string
  expiryDate: string | null
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
    expiry_date: payload.expiryDate,
  })
}

export async function deleteReagentById(id: number): Promise<void> {
  await service.delete(`/api/reagent/delete/${id}`)
}

export async function openReagentById(id: number, openDate: string): Promise<void> {
  await service.post('/api/reagent/open', { id, open_date: openDate })
}
