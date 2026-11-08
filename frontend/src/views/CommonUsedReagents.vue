<template>
  <ReagentList
    :reagents="commonUsedReagents"
    @currentReagentId="openDetailById"
  >
    <template #right-button>
      <van-button
        type="primary"
        @click="requestUse"
      >
        取用
      </van-button>
    </template>
  </ReagentList>
  <ReagentUsePopup
    v-model:show="showUsageDialog"
    @confirm="confirmUsage"
  />
</template>
<script setup lang="ts">
import ReagentList from '@/components/ReagentList.vue'
import { ref, onMounted } from 'vue'
import { getCommonUsedReagents } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import { useUserStore } from '@/stores/user'
import { useReagentActions } from '@/composables/useReagentActions'
import ReagentUsePopup from '@/components/ReagentUsePopup.vue'
const userStore = useUserStore()
const commonUsedReagents = ref<Reagent[]>([])

const fetchCommonUsedReagents = async () => {
  try {
    if (userStore.userId === null) {
      return
    }
    const reagents = await getCommonUsedReagents(userStore.userId)
    commonUsedReagents.value = reagents
    console.log('常用试剂:', reagents)
  } catch (err) {
    console.error('获取常用试剂失败:', err)
  }
}

const {
  showDetailPopup,
  currentReagentId,
  openDetail,
  showUsageDialog,
  confirmUsage,
  requestUse,
  requestDelete,
  showDeleteDialog,
  confirmDelete,
  openReagent,
  requestRestock,
} = useReagentActions(fetchCommonUsedReagents)

const openDetailById = (id: number) => {
  const reagent = commonUsedReagents.value.find((r) => r.id === id)
  if (reagent) openDetail(reagent)
}

onMounted(() => {
  fetchCommonUsedReagents()
})
</script>
