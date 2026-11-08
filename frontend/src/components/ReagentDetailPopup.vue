<template>
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
    </div>
    <div class="action-buttons">
      <slot name="action-buttons" />
    </div>
  </van-popup>
</template>

<script setup lang="ts">
import type { Reagent } from '@/api/reagent'
const props = defineProps<{
  currentReagent?: Reagent
}>()

const showDetailPopup = defineModel<boolean>('show', { default: false })
</script>

<style scoped>
.detail {
  padding-left: 24px;
  padding-top: 12px;
  padding-bottom: 12px;
  padding-right: 12px;
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
</style>
