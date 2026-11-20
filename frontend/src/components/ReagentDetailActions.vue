<template>
  <ReagentDetailPopup
    v-model:show="visible"
    :currentReagent="reagent"
  >
    <template #action-buttons>
      <van-button
        v-if="reagent?.category !== 1"
        type="primary"
        @click="reagent && requestUse(reagent)"
      >
        取用
      </van-button>
      <van-button
        type="danger"
        @click="reagent && requestRestock(reagent.id, !reagent.need2restock)"
      >
        {{ reagent?.need2restock ? '完成补货' : '需要补货' }}
      </van-button>
      <van-button
        v-if="showEdit && !reagent?.useCount"
        type="danger"
        @click="emit('edit')"
      >
        编辑
      </van-button>
      <van-button
        v-if="showDelete"
        type="danger"
        @click="showDeleteDialog = true"
      >
        删除
      </van-button>
    </template>
  </ReagentDetailPopup>

  <ReagentUsePopup
    v-model:show="showUsagePopup"
    @confirm="confirmUsage"
  />
  <DeleteDialog
    v-model:visible="showDeleteDialog"
    @confirm="confirmDelete"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ReagentDetailPopup from '@/components/ReagentDetailPopup.vue'
import ReagentUsePopup from '@/components/ReagentUsePopup.vue'
import DeleteDialog from '@/components/DeleteDialog.vue'
import { deleteReagentById, markReagentNeed2Restock } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import { addReagentUsage } from '@/api/reagentusage'
import { useUserStore } from '@/stores/user'
import { COUNT_BASED_CATEGORIES } from '@/constants/reagent'

const props = withDefaults(
  defineProps<{
    reagent?: Reagent
    showEdit?: boolean
    showDelete?: boolean
  }>(),
  { showEdit: false, showDelete: false },
)

const emit = defineEmits<{
  refresh: []
  edit: []
}>()

const visible = defineModel<boolean>('show', { default: false })
const userStore = useUserStore()

// 危化品/生物试剂按次计数直接记录，其余类别弹窗手动录入用量
const showUsagePopup = ref(false)
const requestUse = async (reagent: Reagent) => {
  if (userStore.userId === null) return
  if (COUNT_BASED_CATEGORIES.has(reagent.category)) {
    try {
      await addReagentUsage(reagent.id, userStore.userId, 0)
      emit('refresh')
    } catch (error) {
      console.error('记录试剂使用失败:', error)
    }
  } else {
    showUsagePopup.value = true
  }
  visible.value = false
}
const confirmUsage = async (usageInput: string) => {
  if (userStore.userId === null || !props.reagent) return
  try {
    await addReagentUsage(props.reagent.id, userStore.userId, Number(usageInput))
    emit('refresh')
    showUsagePopup.value = false
    visible.value = false
  } catch (error) {
    console.error('记录试剂使用失败:', error)
  }
}

const requestRestock = async (reagentId: number, need2restock: boolean) => {
  try {
    await markReagentNeed2Restock(reagentId, need2restock)
    emit('refresh')
    visible.value = false
  } catch (error) {
    console.error('标记需要补货失败:', error)
  }
}

const showDeleteDialog = ref(false)
const confirmDelete = async () => {
  if (!props.reagent) return
  await deleteReagentById(props.reagent.id)
  showDeleteDialog.value = false
  visible.value = false
  emit('refresh')
}
</script>
