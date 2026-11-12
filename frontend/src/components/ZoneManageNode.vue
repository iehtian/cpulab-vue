<template>
  <div class="zone-node">
    <div class="zone-row">
      <van-cell
        :key="area.id"
        :title="area.name"
      >
        <template #right-icon>
          <van-button
            v-if="depth === 0"
            plain
            class="btn"
            type="primary"
            @click="onAdd(area.id)"
            size="small"
          >
            添加分区
          </van-button>
          <van-button
            type="danger"
            name="delete"
            size="small"
            class="btn"
            @click.stop="onDelete(area.id)"
            >删除</van-button
          >
        </template>
      </van-cell>
    </div>

    <div
      v-if="depth === 0"
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
  </div>
</template>

<script setup lang="ts">
import type { Zone } from '@/api/zones'

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
  (e: 'delete', id: number): void
}>()
const onAdd = (id: number) => emit('add', id)
const onDelete = (id: number) => emit('delete', id)
</script>

<style scoped>
.zone-children {
  padding-left: 24px; /* 每层缩进，体现层级 */
}
.zone-node :deep(.van-cell) {
  --van-cell-vertical-padding: 4px; /* 默认 10px，按需调小 */
}
.btn {
  margin-left: 8px;
}
</style>
