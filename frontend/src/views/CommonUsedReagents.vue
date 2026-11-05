<template>
  <ReagentList
    :reagents="commonUsedReagents"
    @update-reagents="fetchCommonUsedReagents"
    @edit-reagent="onReagentEdit"
  />
</template>
<script setup lang="ts">
import ReagentList from '@/components/ReagentList.vue'
import { ref, onMounted } from 'vue'
import { getCommonUsedReagents } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import { useUserStore } from '@/stores/user'
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
const onReagentEdit = (reagent: Reagent) => {
  // 处理试剂编辑逻辑
  console.log('编辑试剂:', reagent)
}
onMounted(() => {
  fetchCommonUsedReagents()
})
</script>
