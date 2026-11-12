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
        :depth="depth + 1"
        :path="path.slice(1)"
        @selected="(e) => emit('selected', e)"
      />
    </van-tab>
  </van-tabs>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { Zone } from '@/api/zones'

defineOptions({
  name: 'ZoneDisplayNode',
})
const props = defineProps<{
  zones: Zone[]
  depth: number
  path: number[]
}>()

const emit = defineEmits<{
  selected: [payload: { depth: number; index: number }]
}>()

const active = computed({
  get: () => props.path[0] ?? 0,
  set: (v) => emit('selected', { depth: props.depth, index: v }),
})
</script>
