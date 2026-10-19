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
      <van-cell-group>
        <van-cell title="空间管理">
          <template #value> <div @click="onAddSpace">添加空间</div> </template>
        </van-cell>
        <van-cell
          v-for="space in spaces"
          :key="space.id"
          :title="space.name"
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
      <van-dialog
        v-model:show="show"
        title="添加空间"
        show-cancel-button
        @confirm="onConfirmAdd"
      >
        <van-field
          v-model="spaceName"
          label="空间名称"
          placeholder="请输入空间名称"
        />
      </van-dialog>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { getAllSpaces, addSpace } from '@/api/manager.ts'
const isMobile = ref(false)
const show = ref(false)
const showActions = ref(false)
const spaceName = ref('')
interface Space {
  id: number
  name: string
}
const spaces = ref<Space[]>([])

const actions = [
  { name: '编辑', color: '#1989fa' },
  { name: '删除', color: '#ee0a24' },
]
const onSelect = (action: { name: string }) => {
  console.log('选择了:', action.name)
  // 在这里根据 action.name 处理对应逻辑
}

onMounted(async () => {
  try {
    const res = await getAllSpaces()
    console.log('获取空间列表成功:', res)
    spaces.value = res
  } catch (err) {
    console.error('获取空间列表失败:', err)
  }
})

const onAddSpace = () => {
  show.value = true
}
const onConfirmAdd = async () => {
  if (!spaceName.value.trim()) {
    // 空名称时不关闭弹窗：vant 中可在 @confirm 里返回 false 阻止关闭
    return false
  }
  try {
    await addSpace(spaceName.value)
    spaceName.value = '' // 成功后重置
  } catch (err) {
    console.error('添加空间失败:', err)
    return false // 失败也阻止关闭
  }
}
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
