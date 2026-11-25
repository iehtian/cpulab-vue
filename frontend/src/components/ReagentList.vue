<template>
  <div
    v-if="reagents.length > 0"
    class="reagent-grid"
  >
    <van-tag
      v-for="reagent in reagents"
      :key="reagent.id"
      size="large"
      plain
      type="primary"
      class="reagent-tag"
      @click="emit('select', reagent.id)"
    >
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
          v-if="
            reagent.category === ReagentCategory.CHROMATOGRAPHY ||
            reagent.category === ReagentCategory.HAZARDOUS
          "
          class="usage-info"
        >
          {{ reagent.lastRemainder ?? '-' }}ml
        </div>
      </div>
    </van-tag>
  </div>
  <van-empty
    v-else
    description="暂无试剂"
    image-size="60"
  />
</template>

<script setup lang="ts">
import type { Reagent } from '@/api/reagent'
import { CATEGORY_MAP, ReagentCategory } from '@/constants/reagent'

defineProps<{ reagents: Reagent[] }>()

const emit = defineEmits<{
  select: [id: number]
}>()
</script>

<style scoped>
.reagent-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 4px;
}
.reagent-tag {
  cursor: pointer;
  --van-tag-large-font-size: 18px;
  --van-tag-large-padding: 10px 20px;
  --van-tag-line-height: 26px;
  box-sizing: border-box;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  font-size: 16px;
}
.tag-info {
  width: 100%;
  min-width: 0;
}
.name-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
}
.name-row .van-tag {
  flex-shrink: 0;
  margin-top: 3px;
}
.reagent-name {
  flex: 1;
  min-width: 0;
  word-break: break-all;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}
.usage-info {
  font-size: 14px;
}
</style>
