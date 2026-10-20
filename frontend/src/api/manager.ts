import service from '@/utils/request'

async function getAllSpaces(): Promise<Array<{ id: number; name: string }>> {
  const response = await service.get(`/api/space/all`)
  const data = response.data
  return data.spaces || []
}

async function deleteSpaceById(id: number): Promise<void> {
  await service.delete(`/api/space/delete/${id}`)
}

async function addSpace(name: string): Promise<void> {
  await service.post(`/api/space/add`, { name })
}

async function addZone(parentId: number | null, spaceId: number, name: string): Promise<void> {
  await service.post(`/api/zone/add`, { parentId, spaceId, name })
}

async function getZonesBySpace(
  spaceId: number,
): Promise<Array<{ id: number; name: string; parentId: number | null }>> {
  const response = await service.get(`/api/zone/all/${spaceId}`)
  const data = response.data
  return data.zones || []
}

export { getAllSpaces, addSpace, deleteSpaceById, addZone, getZonesBySpace }
