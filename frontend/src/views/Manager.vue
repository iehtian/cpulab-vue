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
              @click.stop="((showActions = true), (selectedSpaceId = space.id))"
            /> </template
        ></van-cell>
      </van-cell-group>

      <van-action-sheet
        v-model:show="showActions"
        v-model:id="selectedSpaceId"
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
import { getAllSpaces, addSpace, deleteSpaceById } from '@/api/manager.ts'
import { showDialog } from 'vant'
const isMobile = ref(false)
const show = ref(false)
const showActions = ref(false)
const spaceName = ref('')
const selectedSpaceId = ref<number | null>(null)
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
  console.log('选择了:', action.name, '空间ID:', selectedSpaceId.value)
  if (action.name === '编辑') {
    // 编辑逻辑
  } else if (action.name === '删除') {
    // 删除逻辑
    showDialog({
      title: '确认删除',
      message: '删除后无法恢复，是否继续？',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    }).then(async () => {
      if (selectedSpaceId.value !== null) {
        try {
          await deleteSpaceById(selectedSpaceId.value)
          spaces.value = spaces.value.filter((space) => space.id !== selectedSpaceId.value)
          console.log('删除空间成功:', selectedSpaceId.value)
        } catch (err) {
          console.error('删除空间失败:', err)
        }
      }
    })
  }
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
    getAllSpaces().then((res) => {
      spaces.value = res
    })
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
