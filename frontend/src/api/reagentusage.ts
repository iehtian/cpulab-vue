import service from '@/utils/request'
async function addReagentUsage(reagentId: number, userId: number, amount?: number): Promise<void> {
  await service.post('/api/reagent/usage/add', {
    reagent_id: reagentId,
    user_id: userId,
    amount: amount,
  })
}

export { addReagentUsage }
