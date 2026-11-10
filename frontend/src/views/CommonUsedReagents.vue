<template>
  <van-search
    v-model="searchKeyword"
    placeholder="请输入试剂名称"
  />

  <ReagentList :reagents="showReagents">
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
import { ref, onMounted, computed } from 'vue'
import ReagentList from '@/components/ReagentList.vue'
import ReagentUsePopup from '@/components/ReagentUsePopup.vue'
import { getCommonUsedReagents } from '@/api/reagent'
import type { ReagentTimes } from '@/api/reagent'
import { useUserStore } from '@/stores/user'
import { useReagentActions } from '@/composables/useReagentActions'

const userStore = useUserStore()
const searchKeyword = ref('')
const commonUsedReagents = ref<ReagentTimes[]>([])

const fetchCommonUsedReagents = async () => {
  if (userStore.userId === null) return
  try {
    commonUsedReagents.value = await getCommonUsedReagents(userStore.userId)
  } catch (err) {
    console.error('获取常用试剂失败:', err)
  }
}

const showReagents = computed(() => {
  if (!searchKeyword.value) {
    return commonUsedReagents.value
  }
  return commonUsedReagents.value.filter((reagent) => reagent.name.includes(searchKeyword.value))
})

const { showUsagePopup, requestUse, confirmUsage } = useReagentActions(fetchCommonUsedReagents)

onMounted(fetchCommonUsedReagents)
</script>
