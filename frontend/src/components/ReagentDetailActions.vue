<template>
  <ReagentDetailPopup
    v-model:show="visible"
    :currentReagent="reagent"
  >
    <template #action-buttons>
      <van-button
        v-if="reagent?.category !== ReagentCategory.NORMAL"
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
        type="primary"
        @click="openUsageList"
        >使用记录
      </van-button>
      <van-button
        v-if="showEdit && editable"
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
  <van-popup
    v-model:show="showUsageListPopup"
    position="bottom"
    height="70%"
  >
    <van-list
      v-model:loading="usageLoading"
      :finished="usageFinished"
      finished-text="没有更多了"
      @load="UsageOnLoad"
    >
      <div
        class="usage-row usage-header"
        :class="{ 'usage-row--compact': !showAmountCols }"
      >
        <span>使用人</span>
        <span>使用时间</span>
        <span v-if="showAmountCols">使用量</span>
        <span v-if="showAmountCols">剩余量</span>
      </div>
      <div
        v-for="item in usageList"
        :key="item.id"
        class="usage-row"
        :class="{ 'usage-row--compact': !showAmountCols }"
      >
        <span>{{ item.user_name }}</span>
        <span>{{ item.usage_time.slice(5, 16) }}</span>
        <span v-if="showAmountCols">{{ item.amount != null ? item.amount + 'ml' : '—' }}</span>
        <span v-if="showAmountCols">{{
          item.remaining_after != null ? item.remaining_after + 'ml' : '—'
        }}</span>
      </div>
    </van-list>
  </van-popup>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import ReagentDetailPopup from '@/components/ReagentDetailPopup.vue'
import ReagentUsePopup from '@/components/ReagentUsePopup.vue'
import DeleteDialog from '@/components/DeleteDialog.vue'
import { deleteReagentById, markReagentNeed2Restock } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import { addReagentUsage } from '@/api/reagentusage'
import { useUserStore } from '@/stores/user'
import { COUNT_BASED_CATEGORIES, ReagentCategory } from '@/constants/reagent'
import { getReagentUsage, type ReagentUsage, type ReagentUsageList } from '@/api/reagentusage'
const showUsageListPopup = ref(false)

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

// van-list 在 van-popup 里 immediate-check 时机不可靠（挂载时弹窗还在滑入动画中），
// 改为打开弹窗时手动加载第一页，同时重置状态避免混入上一个试剂的记录
const openUsageList = () => {
  usageList.value = []
  usagePage.value = 1
  usageFinished.value = false
  showUsageListPopup.value = true
  UsageOnLoad()
}
const usageList = ref<ReagentUsage[]>([])
const usagePage = ref(1)
const usageLoading = ref(false)
const usageFinished = ref(false)
const UsageOnLoad = async () => {
  if (!props.reagent) return
  usageLoading.value = true
  try {
    const usageListData: ReagentUsageList = await getReagentUsage(props.reagent.id, usagePage.value)
    usageList.value.push(...usageListData.records)
    usagePage.value += 1
    usageFinished.value = usageListData.records.length < 20
  } catch {
    // 请求失败时停止 van-list 继续触发 load，避免 loading 卡死
    usageFinished.value = true
  } finally {
    usageLoading.value = false
  }
}

const showAmountCols = computed(
  () =>
    props.reagent?.category === ReagentCategory.CHROMATOGRAPHY ||
    props.reagent?.category === ReagentCategory.HAZARDOUS,
)
const editable = ref(false)
watch(
  () => props.reagent,
  async () => {
    editable.value = false
    if (!props.reagent) return
    const usageListData: ReagentUsageList = await getReagentUsage(
      props.reagent?.id,
      usagePage.value,
    )
    editable.value = !usageListData.total
  },
)
</script>

<style scoped>
.usage-row {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  padding: 10px 16px;
  font-size: 14px;
  border-bottom: 1px solid #ebedf0;
  text-align: center;
  align-items: center;
}

.usage-row--compact {
  grid-template-columns: 1fr 2fr;
}

.usage-header {
  position: sticky;
  top: 0;
  background: #f7f8fa;
  font-weight: 600;
  z-index: 1;
}
</style>
