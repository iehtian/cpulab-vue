<template>
  <van-row>
    <van-col
      span="8"
      v-for="r in reagents"
      :key="r.id"
    >
      <div class="reagent-container">
        <van-tag
          size="large"
          :type="tagType(r)"
          class="reagent-tag"
          @click="showDetail(r)"
        >
          {{ r.name }}
          <span
            v-if="r.bottle_count != null"
            class="count"
            >×{{ r.bottle_count }}</span
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
    v-model:show="showPopup"
    round
    position="bottom"
  >
    <div
      class="detail"
      v-if="current"
    >
      <h3>{{ current.name }}</h3>
      <p>CAS 号：{{ current.CAS_number || '-' }}</p>
      <p>规格：{{ current.specification || '-' }}</p>
      <p>容量：{{ current.capacity ?? '-' }}</p>
      <p>瓶数：{{ current.bottle_count ?? '-' }}</p>
      <p>开瓶日期：{{ current.open_date || '-' }}</p>
      <p>有效期：{{ current.expiry_date || '-' }}</p>
    </div>
    <div class="action-buttons">
      <van-button
        type="danger"
        @click="showPopup = false"
        >标记需要补货</van-button
      >
      <van-button
        plain
        type="primary"
        :disabled="!!current?.open_date"
        @click="handleOpen()"
        >开瓶贴标</van-button
      >
      <van-button
        type="danger"
        @click="showPopup = false"
        >编辑</van-button
      >
      <van-button
        type="danger"
        @click="showDelete = true"
        >删除</van-button
      >
    </div>
  </van-popup>
  <DeleteDialog
    v-model:visible="showDelete"
    @confirm="confirmDelete"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { type Reagent } from '@/api/manager.ts'
import { openReagentById, deleteReagentById } from '@/api/manager.ts'
import DeleteDialog from '@/components/DeleteDialog.vue'
const props = defineProps<{ reagents: Reagent[] }>()
const showDelete = ref(false)
const showPopup = ref(false)
const current = ref<Reagent | null>(null)

const emit = defineEmits<{
  updateReagents: []
}>()

function showDetail(r: Reagent) {
  current.value = r
  showPopup.value = true
}

// 按有效期/数量给胶囊着色：临近过期 → warning，数量为 0 → default
function tagType(r: Reagent): 'primary' | 'warning' | 'default' {
  if (r.bottle_count === 0) return 'default'
  if (r.expiry_date && new Date(r.expiry_date).getTime() - Date.now() < 30 * 86400_000)
    return 'warning'
  return 'primary'
}

const handleDelete = async (id: number) => {
  try {
    await deleteReagentById(id)
    // 删除成功后可以触发一个事件或更新父组件的状态
    // 例如 emit('reagentDeleted', id)
  } catch (error) {
    console.error('删除试剂失败:', error)
  }
}

const handleOpen = async () => {
  try {
    await openReagentById(current.value?.id || -1, new Date().toISOString()).then(() => {
      emit('updateReagents') // 通知父组件更新试剂列表
    })
    // 开瓶成功后可以触发一个事件或更新父组件的状态
    // 例如 emit('reagentOpened', id)
    showPopup.value = false // 关闭弹层
  } catch (error) {
    console.error('开瓶失败:', error)
  }
}

const confirmDelete = async () => {
  if (current.value) {
    await handleDelete(current.value.id).then(() => {
      emit('updateReagents') // 通知父组件更新试剂列表
    })
    showDelete.value = false
    showPopup.value = false // 关闭详情弹层
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
.reagent-tag {
  cursor: pointer;
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
