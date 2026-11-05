<template>
  <ReagentList
    :reagents="need2RestockReagents"
    @update-reagents="fetchNeed2RestockReagents"
    @edit-reagent="onReagentEdit"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getNeed2RestockReagents } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import ReagentList from '@/components/ReagentList.vue'

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
const onReagentEdit = (reagent: Reagent) => {
  // 处理试剂编辑逻辑
  console.log('编辑试剂:', reagent)
}

onMounted(() => {
  fetchNeed2RestockReagents()
})
</script>
