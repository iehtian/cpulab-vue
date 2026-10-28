import service from '@/utils/request'

export interface Space {
  id: number
  name: string
}

export async function getAllSpaces(): Promise<Space[]> {
  const response = await service.get('/api/space/all')
  return response.data.spaces || []
}

export async function addSpace(name: string): Promise<void> {
  await service.post('/api/space/add', { name })
}

export async function deleteSpaceById(id: number): Promise<void> {
  await service.delete(`/api/space/delete/${id}`)
}
