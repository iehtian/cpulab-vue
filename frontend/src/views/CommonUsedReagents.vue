<template>
  <van-search
    v-model="searchKeyword"
    placeholder="请输入试剂名称"
  />

  <ReagentList
    :reagents="showReagents"
    @select="openDetailById"
  />
  <ReagentDetailActions
    v-model:show="showDetailPopup"
    :reagent="currentReagent"
    @refresh="fetchCommonUsedReagents"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import ReagentList from '@/components/ReagentList.vue'
import ReagentDetailActions from '@/components/ReagentDetailActions.vue'
import { getCommonUsedReagents } from '@/api/reagent'
import type { ReagentTimes } from '@/api/reagent'
import { useUserStore } from '@/stores/user'

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

const showDetailPopup = ref(false)
const currentReagentId = ref(-1)
const currentReagent = computed(() =>
  commonUsedReagents.value.find((r) => r.id === currentReagentId.value),
)
const openDetailById = (id: number) => {
  currentReagentId.value = id
  showDetailPopup.value = true
}

onMounted(fetchCommonUsedReagents)
</script>
