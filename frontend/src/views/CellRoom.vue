<template>
  <DeviceReservation v-if="!isMobile" />
  <DeviceReservation_mobile v-else />
</template>
<script setup lang="ts">
import DeviceReservation from '@/views/DeviceReservation.vue'
import DeviceReservation_mobile from '@/views/DeviceReservation_mobile.vue'
import { useViewportStore } from '@/stores/viewport'

const viewportStore = useViewportStore()
const isMobile = viewportStore.isMobile
</script>
