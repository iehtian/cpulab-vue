import { ref } from 'vue'
import { openReagentById, deleteReagentById, markReagentNeed2Restock } from '@/api/reagent'
import { addReagentUsage } from '@/api/reagentusage'
import type { Reagent } from '@/api/reagent'
import { useUserStore } from '@/stores/user'

export function useReagentActions(refresh: () => void) {
  const userStore = useUserStore()

  const showDetailPopup = ref(false)
  const currentReagentId = ref(-1)

  const openDetail = (reagent: Reagent) => {
    currentReagentId.value = reagent.id
    showDetailPopup.value = true
  }
  const closeDetail = () => {
    showDetailPopup.value = false
    currentReagentId.value = -1
  }

  const showDeleteDialog = ref(false)
  const requestDelete = () => {
    showDeleteDialog.value = true
  }
  const confirmDelete = async () => {
    if (currentReagentId.value === -1) return
    await deleteReagentById(currentReagentId.value)
    showDeleteDialog.value = false
    closeDetail()
    refresh()
  }

  const showUsagePopup = ref(false)
  const requestUse = async (reagent: Reagent) => {
    if (userStore.userId === null) return
    currentReagentId.value = reagent.id
    // 危化品/生物试剂按次计数，其余类别弹窗手动录入用量
    if (reagent.category === 2 || reagent.category === 3) {
      try {
        await addReagentUsage(reagent.id, userStore.userId, 0)
        refresh()
      } catch (error) {
        console.error('记录试剂使用失败:', error)
      }
    } else {
      showUsagePopup.value = true
    }
    showDetailPopup.value = false
  }
  const confirmUsage = async (usageInput: string) => {
    if (userStore.userId === null) return
    try {
      await addReagentUsage(currentReagentId.value, userStore.userId, Number(usageInput))
      refresh()
      showUsagePopup.value = false
      showDetailPopup.value = false
    } catch (error) {
      console.error('记录试剂使用失败:', error)
    }
  }

  const openReagent = async () => {
    if (userStore.userId === null) return
    try {
      await openReagentById(currentReagentId.value, new Date().toISOString(), userStore.userId)
      refresh()
      showDetailPopup.value = false
    } catch (error) {
      console.error('打开试剂失败:', error)
    }
  }

  const requestRestock = async (reagentId: number, need2restock: boolean) => {
    try {
      await markReagentNeed2Restock(reagentId, need2restock)
      refresh()
      showDetailPopup.value = false
    } catch (error) {
      console.error('标记需要补货失败:', error)
    }
  }

  return {
    showDetailPopup,
    currentReagentId,
    openDetail,
    closeDetail,
    showDeleteDialog,
    requestDelete,
    confirmDelete,
    showUsagePopup,
    requestUse,
    confirmUsage,
    openReagent,
    requestRestock,
  }
}
