<template>
  <div>
    <div class="container nav_buttons">
      <van-button
        plain
        square
        v-for="id in 8"
        >朴素按钮</van-button
      >
    </div>
    <router-view />
    <div class="container space">
      ><van-cell-group>
        <van-cell title="空间管理">
          <template #value> <div @click="onAddSpace">添加空间</div> </template>
        </van-cell>
        <van-cell
          title="单元格"
          value="内容"
          label="描述信息"
          to="/Spaces"
        >
          <template #right-icon>
            <van-icon
              name="ellipsis"
              class="more-icon"
              @click.stop="showActions = true"
            /> </template
        ></van-cell>
      </van-cell-group>
      <van-action-sheet
        v-model:show="showActions"
        :actions="actions"
        cancel-text="取消"
        close-on-click-action
        @select="onSelect"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { getAllSpaces } from '@/api/manager.ts'
const isMobile = ref(false)
const showActions = ref(false)
const actions = [
  { name: '编辑', color: '#1989fa' },
  { name: '删除', color: '#ee0a24' },
]
const onSelect = (action: { name: string }) => {
  console.log('选择了:', action.name)
  // 在这里根据 action.name 处理对应逻辑
}
const onAddSpace = () => {
  console.log('添加空间按钮被点击')
  // 在这里处理添加空间的逻辑
}
onMounted(async () => {
  try {
    const res = await getAllSpaces()
    console.log('获取空间列表成功:', res)
  } catch (err) {
    console.error('获取空间列表失败:', err)
  }
})
</script>

<style scoped>
.van-cell-group--inset {
  margin: 1rem;
}
.container {
  background-color: aliceblue;
  border-radius: 8px;
}
.nav_buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto;
}
.container :deep(.van-button) {
  margin: 0;
  border: none;
}
.more-icon {
  transform: rotate(90deg);
  font-size: 18px;
  color: #969799;
  padding: 4px;
}
</style>
