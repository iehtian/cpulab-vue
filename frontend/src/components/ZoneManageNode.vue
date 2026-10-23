<template>
  <div class="zone-node">
    <div class="zone-row">
      <van-cell
        :key="area.id"
        :title="area.name"
        value="内容"
      />
    </div>

    <!-- 递归渲染 children，用 padding-left 体现层级 -->
    <div
      v-if="area.children?.length"
      class="zone-children"
    >
      <ZoneNode
        v-for="child in area.children"
        :key="child.id"
        :area="child"
        :depth="depth + 1"
        @add="onAdd"
      />
    </div>
    <van-button
      plain
      type="primary"
      @click="onAdd(area.id)"
      v-if="depth < 1"
    >
      添加分区
    </van-button>
  </div>
</template>

<script setup lang="ts">
import type { Zone } from '@/api/manager.ts'
import { defineOptions } from 'vue'

// script setup 下要递归引用自己，必须通过 name 选项
defineOptions({ name: 'ZoneNode' })

withDefaults(
  defineProps<{
    area: Zone
    depth?: number
  }>(),
  {
    depth: 0,
  },
)

const emit = defineEmits<{
  (e: 'add', parentId: number): void
}>()
const onAdd = (id: number) => emit('add', id)
</script>

<style scoped>
.zone-children {
  padding-left: 24px; /* 每层缩进，体现层级 */
}
</style>
