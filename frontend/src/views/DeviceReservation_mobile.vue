<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; align-items: center">
      <el-date-picker
        v-model="Monday"
        type="week"
        format="YYYY-MM-DD"
        placeholder="请选择周"
      />
      <el-button-group class="mb-4">
        <el-button
          type="primary"
          :icon="ArrowLeft"
          @click="prevWeek"
          >Previous</el-button
        >
        <el-button
          type="primary"
          @click="resetWeek"
          >This</el-button
        >
        <el-button
          type="primary"
          @click="nextWeek"
        >
          Next<el-icon class="el-icon--right">
            <ArrowRight />
          </el-icon>
        </el-button>
      </el-button-group>
    </div>
  </el-card>
  <div class="grid-scroll">
    <div class="day-grid">
      <div
        v-for="slottime of 32"
        class="grid-cell grid-corner booking-slot"
        :class="[
          {
            // ispast: isPastBlock(slottime),
            // selected: isSelected(slottime),
            // is_ordered: is_order(slottime),
          },
        ]"
      >
        <div class="slot-time">{{ slottime }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.day-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(8, 1fr);
  border-left: var(--el-border);
  border-top: var(--el-border);
}
.booking-slot {
  background: #effaf3;
  /* height: 26px; */
}
</style>
