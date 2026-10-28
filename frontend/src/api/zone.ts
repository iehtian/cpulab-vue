import service from '@/utils/request'

export interface Zone {
  id: number
  name: string
  parent_id: number
  sort_order: number | null
  children?: Zone[]
}

export async function getZonesBySpace(spaceId: number): Promise<Zone[]> {
  const response = await service.get(`/api/zone/all/${spaceId}`)
  return response.data.zones || []
}

export async function addZone(parentId: number | null, spaceId: number, name: string): Promise<void> {
  await service.post('/api/zone/add', { parent_id: parentId, space_id: spaceId, name })
}
