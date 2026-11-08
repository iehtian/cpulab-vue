<template>
  <ReagentList
    :reagents="need2RestockReagents"
    @currentReagentId="openDetailById"
  >
    <template #right-button>
      <van-button
        type="primary"
        @click="requestRestock(false)"
      >
        补货
      </van-button>
    </template>
  </ReagentList>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getNeed2RestockReagents } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import ReagentList from '@/components/ReagentList.vue'
import { useReagentActions } from '@/composables/useReagentActions'

const need2RestockReagents = ref<Reagent[]>([])

const fetchNeed2RestockReagents = async () => {
  try {
    const reagents = await getNeed2RestockReagents()
    need2RestockReagents.value = reagents
    console.log('需要补货的试剂:', reagents)
  } catch (err) {
    console.error('获取需要补货的试剂失败:', err)
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
} = useReagentActions(fetchNeed2RestockReagents)

const openDetailById = (id: number) => {
  const reagent = need2RestockReagents.value.find((r) => r.id === id)
  if (reagent) openDetail(reagent)
}

onMounted(() => {
  fetchNeed2RestockReagents()
})
</script>
