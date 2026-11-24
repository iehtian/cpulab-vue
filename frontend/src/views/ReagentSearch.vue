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
    @refresh="fetchallReagents"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import ReagentList from '@/components/ReagentList.vue'
import ReagentDetailActions from '@/components/ReagentDetailActions.vue'
import { getAllReagents ,type Reagent} from '@/api/reagent'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const searchKeyword = ref('')
const allReagents = ref<Reagent[]>([])

const fetchallReagents = async () => {
  if (userStore.userId === null) return
  try {
    allReagents.value = await getAllReagents()
  } catch (err) {
    console.error('获取常用试剂失败:', err)
  }
}

const showReagents = computed(() => {
  if (!searchKeyword.value) {
    return allReagents.value
  }
  return allReagents.value.filter((reagent) => reagent.name.includes(searchKeyword.value))
})

const showDetailPopup = ref(false)
const currentReagentId = ref(-1)
const currentReagent = computed(() =>
  allReagents.value.find((r) => r.id === currentReagentId.value),
)
const openDetailById = (id: number) => {
  currentReagentId.value = id
  showDetailPopup.value = true
}

onMounted(fetchallReagents)
</script>
