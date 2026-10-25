<template>
  <van-tabs v-model:active="active">
    <van-tab
      v-for="zone in zones"
      :key="zone.id"
      :title="zone.name"
    >
      <ZoneDisplayNode
        v-if="zone.children?.length"
        :zones="zone.children"
        @update:zoneid="(id) => emit('update:zoneid', id)"
      />
    </van-tab>
  </van-tabs>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Zone } from '@/api/manager.ts'

defineOptions({
  name: 'ZoneDisplayNode',
})
const props = defineProps<{
  zones: Zone[]
}>()

const emit = defineEmits<{
  (e: 'update:zoneid', id: number): void
}>()

const active = ref(0)
watch(active, (idx) => {
  const zone = props.zones[idx]
  // 选中的是叶子节点（没有子分区）才把 id 往上抛
  if (zone && !zone.children?.length) {
    emit('update:zoneid', zone.id)
  }
})
</script>
