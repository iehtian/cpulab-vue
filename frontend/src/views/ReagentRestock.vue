<template>
  <van-search
    v-model="searchKeyword"
    placeholder="请输入试剂名称"
  />
  <ReagentList :reagents="showReagents">
    <template #right-button="{ reagent }">
      <van-button
        type="primary"
        @click="requestRestock(reagent.id, false)"
      >
        补货
      </van-button>
    </template>
  </ReagentList>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import ReagentList from '@/components/ReagentList.vue'
import { getNeed2RestockReagents } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import { useReagentActions } from '@/composables/useReagentActions'

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

const { requestRestock } = useReagentActions(fetchNeed2RestockReagents)

onMounted(fetchNeed2RestockReagents)
</script>
