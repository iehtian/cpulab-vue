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
      />
    </van-tab>
  </van-tabs>
</template>

<script setup lang="ts">
import { ref, defineOptions } from 'vue'
import type { Zone } from '@/api/manager.ts'

defineOptions({
  name: 'ZoneDisplayNode',
})
defineProps<{
  zones: Zone[]
}>()
const active = ref(0)
</script>
