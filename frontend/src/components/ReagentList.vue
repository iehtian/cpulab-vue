<template>
  <van-row v-if="reagents.length > 0">
    <van-col
      v-for="reagent in reagents"
      :key="reagent.id"
      span="12"
    >
      <div class="reagent-container">
        <van-tag
          size="large"
          plain
          type="primary"
          class="reagent-tag"
          @click="emit('select', reagent.id)"
        >
          <div class="tag-row">
            <div class="tag-info">
              <div class="name-row">
                <span class="reagent-name">{{ reagent.name }}</span>
                <van-tag
                  :type="CATEGORY_MAP[reagent.category]?.type ?? 'default'"
                  plain
                  round
                >
                  {{ CATEGORY_MAP[reagent.category]?.text ?? '未知' }}
                </van-tag>
              </div>
              <div
                v-if="COUNT_BASED_CATEGORIES.has(reagent.category)"
                class="usage-info"
              >
                {{ reagent.usageLength ?? 0 }} 次，最近
                {{ reagent.lastUserName ?? '-' }}
              </div>
              <div
                v-else-if="reagent.category === ReagentCategory.CHROMATOGRAPHY"
                class="usage-info"
              >
                {{ reagent.lastRemainder ?? '-' }}ml，最近{{ reagent.lastUserName ?? '-' }}
              </div>
              <div
                v-else
                class="usage-info"
              >
                -
              </div>
            </div>
          </div>
        </van-tag>
      </div>
    </van-col>
  </van-row>
  <van-empty
    v-else
    description="暂无试剂"
    image-size="60"
  />
</template>

<script setup lang="ts">
import type { Reagent } from '@/api/reagent'
import { CATEGORY_MAP, COUNT_BASED_CATEGORIES, ReagentCategory } from '@/constants/reagent'

defineProps<{ reagents: Reagent[] }>()

const emit = defineEmits<{
  select: [id: number]
}>()
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
.tag-row {
  display: flex;
  align-items: center; /* 按钮垂直居中 */
  justify-content: space-between;
  width: 100%;
  gap: 8px;
}
.tag-action {
  flex-shrink: 0; /* 不被压缩 */
  margin-left: auto; /* 无论左侧内容多长，都推到最右 */
}
.tag-info {
  min-width: 0; /* 允许收缩，内部名字才能触发省略号 */
}
.name-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.usage-info {
  font-size: 14px;
}
.reagent-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
