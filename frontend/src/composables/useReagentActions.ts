// composable 内部
import { useUserStore } from '@/stores/user'
import { ref, computed } from 'vue'
import { openReagentById, deleteReagentById, markReagentNeed2Restock } from '@/api/reagent'
import { addReagentUsage } from '@/api/reagentusage'
import type { Reagent } from '@/api/reagent'

export function useReagentActions(refresh: () => void) {
  const userStore = useUserStore()
  const showDetailPopup = ref(false)
  const showDeleteDialog = ref(false)

  const currentReagentId = ref<number>(-1)
  const openDetail = (reagent: Reagent) => {
    currentReagentId.value = reagent.id
    showDetailPopup.value = true
  }
  const closeDetail = () => {
    showDetailPopup.value = false
    currentReagentId.value = -1
  }
  const requestDelete = () => {
    showDeleteDialog.value = true
  }
  const confirmDelete = async () => {
    if (currentReagentId.value !== -1) {
      await deleteReagentById(currentReagentId.value)
      showDeleteDialog.value = false
      closeDetail()
      refresh()
    }
  }

  const showUsageDialog = ref(false)
  const requestUse = async (reagent: Reagent) => {
    if (userStore.userId === null) return
    console.log('reagent.category', reagent.category)
    if (reagent.category === 2 || reagent.category === 3) {
      try {
        await addReagentUsage(reagent.id, userStore.userId, 0)
        refresh()
        showDetailPopup.value = false
      } catch (error) {
        console.error('记录试剂使用失败:', error)
      }
    } else {
      showUsageDialog.value = true
    }
    showDetailPopup.value = false
  }

  const confirmUsage = async (usageInput: string) => {
    if (userStore.userId === null) return
    try {
      await addReagentUsage(currentReagentId.value, userStore.userId, Number(usageInput))
      refresh()
      showUsageDialog.value = false
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
  const requestRestock = async (need2restock: boolean) => {
    if (userStore.userId === null) return
    try {
      await markReagentNeed2Restock(currentReagentId.value, need2restock)
      refresh()
      showDetailPopup.value = false
    } catch (error) {
      console.error('标记需要补货失败:', error)
    }
  }

  return {
    showDetailPopup,
    showDeleteDialog,
    currentReagentId,
    openDetail,
    closeDetail,
    requestDelete,
    confirmDelete,
    showUsageDialog,
    requestUse,
    confirmUsage,
    openReagent,
    requestRestock,
  }
}
