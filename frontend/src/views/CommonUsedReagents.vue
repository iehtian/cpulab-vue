<template>
  <ReagentList :reagents="commonUsedReagents">
    <template #right-button="{ reagent }">
      <van-button
        type="primary"
        @click="requestUse(reagent)"
      >
        取用
      </van-button>
    </template>
  </ReagentList>
  <ReagentUsePopup
    v-model:show="showUsagePopup"
    @confirm="confirmUsage"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ReagentList from '@/components/ReagentList.vue'
import ReagentUsePopup from '@/components/ReagentUsePopup.vue'
import { getCommonUsedReagents } from '@/api/reagent'
import type { ReagentTimes } from '@/api/reagent'
import { useUserStore } from '@/stores/user'
import { useReagentActions } from '@/composables/useReagentActions'

const userStore = useUserStore()
const commonUsedReagents = ref<ReagentTimes[]>([])

const fetchCommonUsedReagents = async () => {
  if (userStore.userId === null) return
  try {
    commonUsedReagents.value = await getCommonUsedReagents(userStore.userId)
  } catch (err) {
    console.error('获取常用试剂失败:', err)
  }
}

const { showUsagePopup, requestUse, confirmUsage } = useReagentActions(fetchCommonUsedReagents)

onMounted(fetchCommonUsedReagents)
</script>
