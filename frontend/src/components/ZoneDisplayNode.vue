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
        @update:zone-id="(id) => emit('update:zoneId', id)"
      />
    </van-tab>
  </van-tabs>
</template>
<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import type { Zone } from '@/api/zone'

defineOptions({
  name: 'ZoneDisplayNode',
})
const props = defineProps<{
  zones: Zone[]
}>()

const emit = defineEmits<{
  (e: 'update:zoneId', id: number): void
}>()

const active = ref(0)
watchEffect(() => {
  // 自动追踪读取到的所有响应式依赖：active 和 props.zones
  const zone = props.zones[active.value]
  if (zone && !zone.children?.length) {
    emit('update:zoneId', zone.id)
  }
})
</script>
