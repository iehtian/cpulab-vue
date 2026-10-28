<template>
  <!-- <DeviceReservation v-if="!isMobile" /> -->
  <DeviceReservationMobile />
</template>
<script setup lang="ts">
import DeviceReservation from '@/views/DeviceReservation.vue'
import DeviceReservationMobile from '@/views/DeviceReservationMobile.vue'
import { useViewportStore } from '@/stores/viewport'

const viewportStore = useViewportStore()
const isMobile = viewportStore.isMobile
</script>
