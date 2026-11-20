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
    @refresh="fetchNeed2RestockReagents"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import ReagentList from '@/components/ReagentList.vue'
import ReagentDetailActions from '@/components/ReagentDetailActions.vue'
import { getNeed2RestockReagents } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'

const need2RestockReagents = ref<Reagent[]>([])

const fetchNeed2RestockReagents = async () => {
  try {
    need2RestockReagents.value = await getNeed2RestockReagents()
  } catch (err) {
    console.error('获取需要补货的试剂失败:', err)
  }
}

const searchKeyword = ref('')
const showReagents = computed(() => {
  if (!searchKeyword.value) {
    return need2RestockReagents.value
  }
  return need2RestockReagents.value.filter((reagent) => reagent.name.includes(searchKeyword.value))
})

const showDetailPopup = ref(false)
const currentReagentId = ref(-1)
const currentReagent = computed(() =>
  need2RestockReagents.value.find((r) => r.id === currentReagentId.value),
)
const openDetailById = (id: number) => {
  currentReagentId.value = id
  showDetailPopup.value = true
}

onMounted(fetchNeed2RestockReagents)
</script>
