<template>
  <van-row>
    <van-col
      span="8"
      v-for="reagent in reagents"
      :key="reagent.id"
    >
      <div class="reagent-container">
        <van-tag
          size="large"
          :type="tagType(reagent)"
          class="reagent-tag"
          @click="showDetail(reagent)"
        >
          {{ reagent.name }}
          <span
            v-if="reagent.bottle_count != null"
            class="count"
            >×{{ reagent.bottle_count }}</span
          >
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
      <p>CAS 号：{{ currentReagent.CAS_number || '-' }}</p>
      <p>规格：{{ currentReagent.specification || '-' }}</p>
      <p>容量：{{ currentReagent.capacity ?? '-' }}</p>
      <p>瓶数：{{ currentReagent.bottle_count ?? '-' }}</p>
      <p>开瓶日期：{{ currentReagent.open_date || '-' }}</p>
      <p>有效期：{{ currentReagent.expiry_date || '-' }}</p>
    </div>
    <div class="action-buttons">
      <van-button
        type="primary"
        @click="handleReagentUsed()"
        v-if="currentReagent?.category === 2"
        >取用</van-button
      >
      <van-button
        type="danger"
        @click="showDetailPopup = false"
        >标记需要补货</van-button
      >
      <van-button
        plain
        type="primary"
        :disabled="!!currentReagent?.open_date"
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
  <DeleteDialog
    v-model:visible="showDeleteDialog"
    @confirm="confirmDelete"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { openReagentById, deleteReagentById } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'
import DeleteDialog from '@/components/DeleteDialog.vue'
import { addReagentUsage } from '@/api/reagentusage'
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()
defineProps<{ reagents: Reagent[] }>()

const emit = defineEmits<{
  updateReagents: []
}>()

const showDetailPopup = ref(false)
const showDeleteDialog = ref(false)
const currentReagent = ref<Reagent>(null as unknown as Reagent) // 初始化为 null，但类型为 Reagent

function showDetail(reagent: Reagent) {
  currentReagent.value = reagent
  showDetailPopup.value = true
}

// 按有效期/数量给胶囊着色：临近过期 → warning，数量为 0 → default
function tagType(reagent: Reagent): 'primary' | 'warning' | 'default' {
  if (reagent.bottle_count === 0) return 'default'
  if (reagent.expiry_date && new Date(reagent.expiry_date).getTime() - Date.now() < 30 * 86400_000)
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

const handleReagentUsed = async (amount?: number) => {
  try {
    if (!currentReagent.value?.id || userStore.userId === null) {
      return
    }
    await addReagentUsage(currentReagent.value.id, userStore.userId, amount) // 假设 userId 为 1
    emit('updateReagents') // 通知父组件更新试剂列表
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
  margin: 8px 0;
  color: #666;
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
}
.action-buttons {
  display: flex;
  gap: 8px; /* 按钮之间的间隔 */
  padding: 0 24px 24px; /* 与上面 .detail 的内边距对齐 */
  flex-wrap: wrap; /* 屏幕窄时自动换行 */
}
</style>
