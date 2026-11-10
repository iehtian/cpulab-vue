import service from '@/utils/request'
interface ReagentUsage {
  id: number
  reagent_id: number
  user_name: string
  amount?: number
  remaining_after?: number
  usage_time: string
}
interface ReagentUsageList {
  total: number
  records: ReagentUsage[]
}
async function addReagentUsage(reagentId: number, userId: number, amount?: number): Promise<void> {
  await service.post('/api/reagent/usage/add', {
    reagent_id: reagentId,
    user_id: userId,
    amount: amount,
  })
}

async function getReagentUsage(reagentId: number, page: number): Promise<ReagentUsageList> {
  const response = await service.get(`/api/reagent/usage/list`, {
    params: {
      reagent_id: reagentId,
      page: page,
      page_size: 20,
    },
  })

  return response.data.usage_list
}

export { addReagentUsage, getReagentUsage, type ReagentUsage, type ReagentUsageList }
