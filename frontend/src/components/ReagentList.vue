<template>
  <van-row>
    <van-col
      span="12"
      v-for="reagent in reagents"
      :key="reagent.id"
    >
      <div class="reagent-container">
        <van-tag
          size="large"
          plain
          :type="tagType(reagent)"
          class="reagent-tag"
          @click="showDetail(reagent)"
        >
          {{ reagent.name }}
          <div v-if="reagent.category === 1">常规试剂</div>
          <div v-else-if="reagent.category === 2 || reagent.category == 3">
            {{ reagent.usageLength ?? 0 }} 次，最近
            {{ reagent.lastUserName ?? '-' }}
          </div>
          <div v-else>
            <div v-if="reagent.openDate">
              剩余{{ reagent.lastRemainder ?? '-' }}ml，最近{{ reagent.lastUserName ?? '-' }}
            </div>
            <div v-else>尚未开瓶</div>
          </div>
        </van-tag>
        <van-empty
          v-if="reagents.length === 0"
          description="暂无试剂"
          image-size="60"
        />
      </div>
    </van-col>
  </van-row>

  <!-- 详情弹层 -->
  <van-popup
    v-model:show="showDetailPopup"
    round
    position="bottom"
  >
    <div
      class="detail"
      v-if="currentReagent"
    >
      <h3>{{ currentReagent.name }}</h3>
      <p><span class="label">CAS 号：</span>{{ currentReagent.casNumber || '-' }}</p>
      <p><span class="label">规格：</span>{{ currentReagent.specification || '-' }}</p>
      <p><span class="label">容量：</span>{{ currentReagent.capacity ?? '-' }}</p>
      <p><span class="label">瓶数：</span>{{ currentReagent.bottleCount ?? '-' }}</p>
      <p><span class="label">需要补货：</span>{{ currentReagent.need2restock ?? '-' }}</p>
      <p><span class="label">开瓶日期：</span>{{ currentReagent.openDate || '-' }}</p>
      <p><span class="label">有效期：</span>{{ currentReagent.expiryDate || '-' }}</p>
    </div>
    <div class="action-buttons">
      <van-button
        type="primary"
        @click="handleReagentUsed()"
        v-if="currentReagent?.category !== 1"
        :disabled="!currentReagent?.openDate"
        >取用</van-button
      >
      <van-button
        type="danger"
        @click="handleneed2restock()"
        ><p v-if="currentReagent?.need2restock === false">标记需要补货</p>
        <p v-else>完成补货</p>
      </van-button>
      <van-button
        plain
        type="primary"
        :disabled="!!currentReagent?.openDate"
        @click="handleOpen()"
        >开瓶贴标</van-button
      >
      <van-button
        type="danger"
        @click="showDetailPopup = false"
        >编辑</van-button
      >
      <van-button
        type="danger"
        @click="showDeleteDialog = true"
        >删除</van-button
      >
    </div>
  </van-popup>
  <van-dialog
    v-model:show="showUsageDialog"
    title="提示"
    show-cancel-button
    confirm-button-text="确定"
    :confirm-button-disabled="!isUsageValid"
    @confirm="confirmUsage"
  >
    <van-field
      v-model="usageInput"
      type="digit"
      label="记录用量"
      placeholder="请输入用量（ml）"
      :formatter="onlyNumber"
    />
  </van-dialog>

  <DeleteDialog
    v-model:visible="showDeleteDialog"
    @confirm="confirmDelete"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { openReagentById, deleteReagentById, markReagentNeed2Restock } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import DeleteDialog from '@/components/DeleteDialog.vue'
import { addReagentUsage, getReagentUsage } from '@/api/reagentusage'
import { useUserStore } from '@/stores/user'
import { showDialog } from 'vant'
const userStore = useUserStore()
const props = defineProps<{ reagents: Reagent[] }>()

const emit = defineEmits<{
  updateReagents: []
}>()

const showDetailPopup = ref(false)
const showDeleteDialog = ref(false)
const currentReagentId = ref<number | null>(null)

const currentReagent = computed(
  () => props.reagents.find((r) => r.id === currentReagentId.value) ?? null,
)

function showDetail(reagent: Reagent) {
  currentReagentId.value = reagent.id
  showDetailPopup.value = true
}

// 按有效期/数量给胶囊着色：临近过期 → warning，数量为 0 → default
function tagType(reagent: Reagent): 'primary' | 'warning' | 'default' {
  if (reagent.bottleCount === 0) return 'default'
  if (reagent.expiryDate && new Date(reagent.expiryDate).getTime() - Date.now() < 30 * 86400_000)
    return 'warning'
  return 'primary'
}

const handleDelete = async (id: number) => {
  try {
    await deleteReagentById(id)
  } catch (error) {
    console.error('删除试剂失败:', error)
  }
}

const handleneed2restock = async () => {
  try {
    if (!currentReagentId?.value || !currentReagent.value?.need2restock) {
      return
    }

    await markReagentNeed2Restock(currentReagentId.value, !currentReagent.value.need2restock)
    emit('updateReagents') // 通知父组件更新试剂列表
  } catch (error) {
    console.error('标记需要补货失败:', error)
  }
}

const handleOpen = async () => {
  try {
    if (!currentReagent.value?.id || userStore.userId === null) {
      return
    }
    await openReagentById(currentReagent.value.id, new Date().toISOString(), userStore.userId)
    emit('updateReagents') // 通知父组件更新试剂列表
    showDetailPopup.value = false
  } catch (error) {
    console.error('开瓶失败:', error)
  }
}

const confirmDelete = async () => {
  if (currentReagent.value) {
    await handleDelete(currentReagent.value.id)
    emit('updateReagents') // 通知父组件更新试剂列表
    showDeleteDialog.value = false
    showDetailPopup.value = false // 关闭详情弹层
  }
}

const showUsageDialog = ref(false)
const usageInput = ref('')

// 输入合法才允许点确认
const isUsageValid = computed(() => {
  const n = Number(usageInput.value)
  return usageInput.value !== '' && Number.isFinite(n) && n > 0
})

// 限制只能输入数字（整数）
const onlyNumber = (value: string) => value.replace(/[^\d]/g, '')

const handleReagentUsed = async () => {
  if (!currentReagent.value?.id || userStore.userId === null) return
  const reagent = currentReagent.value
  if (reagent.category === 2 || reagent.category === 3) {
    try {
      await addReagentUsage(reagent.id, userStore.userId, 0)
      emit('updateReagents')
      showDetailPopup.value = false
    } catch (error) {
      console.error('记录试剂使用失败:', error)
    }
  } else {
    usageInput.value = '' // 每次打开重置输入
    showUsageDialog.value = true
  }
  showDetailPopup.value = false
}

const confirmUsage = async () => {
  if (!currentReagent.value || userStore.userId === null || !isUsageValid.value) return
  try {
    await addReagentUsage(currentReagent.value.id, userStore.userId, Number(usageInput.value))
    emit('updateReagents')
    showDetailPopup.value = false
  } catch (error) {
    console.error('记录试剂使用失败:', error)
  }
}
</script>

<style scoped>
.reagent-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px;
}
.count {
  opacity: 0.7;
  margin-left: 2px;
}
.detail {
  padding: 24px;
}
.detail h3 {
  margin-top: 0;
}
.detail p {
  display: flex;
  margin: 8px 0;
  color: #666;
}
.detail .label {
  flex: 0 0 5em; /* 不伸不缩，所有标签固定占 5em，值的起点对齐 */
}
.reagent-tag {
  cursor: pointer;
  /* 放大字号和内边距，tag 的高度 = 行高 + 上下内边距 */
  --van-tag-large-font-size: 18px;
  --van-tag-large-padding: 10px 20px;
  --van-tag-line-height: 26px;
  width: 100%; /* 充满父容器（.reagent-container / van-col） */
  justify-content: center; /* 文字在 tag 内居中 */
  box-sizing: border-box; /* 让内边距算在 100% 宽度内，避免溢出 */
  flex-direction: column;
  align-items: flex-start;
  font-size: 16px;
}
.action-buttons {
  display: flex;
  gap: 8px; /* 按钮之间的间隔 */
  padding: 0 24px 24px; /* 与上面 .detail 的内边距对齐 */
  flex-wrap: wrap; /* 屏幕窄时自动换行 */
}
/* 让 badge 的包装层撑满 van-col，恢复原来块级布局 :deep(.van-badge__wrapper) {
  display: block;
  width: 95%;
} */
</style>
