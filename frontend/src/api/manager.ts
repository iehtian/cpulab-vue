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

async function addArea(parentId: number | null, spaceId: number, name: string): Promise<void> {
  await service.post(`/api/area/add`, { parentId, spaceId, name })
}

async function getAreasBySpace(
  spaceId: number,
): Promise<Array<{ id: number; name: string; parentId: number | null }>> {
  const response = await service.get(`/api/area/all/${spaceId}`)
  const data = response.data
  return data.areas || []
}

export { getAllSpaces, addSpace, deleteSpaceById, addArea, getAreasBySpace }
