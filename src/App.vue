<script setup lang="ts">
  import { RouterLink, RouterView } from 'vue-router'
  import HelloWorld from './components/HelloWorld.vue'
  import ButtonExample from './components/button.vue'
  import OnedayExample from './components/oneday.vue'

</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/reservation">设备预约</RouterLink>
        <RouterLink to="/DeviceReservation_bak">设备预约备份</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>
