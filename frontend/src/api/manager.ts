import service from '@/utils/request'

async function getAllSpaces(): Promise<Array<{ id: number; name: string }>> {
  const response = await service.get(`/api/space/all`)
  const data = response.data
  return data.spaces || []
}

async function addSpace(name: string): Promise<void> {
  await service.post(`/api/space/upsert`, { name })
}

export { getAllSpaces, addSpace }
