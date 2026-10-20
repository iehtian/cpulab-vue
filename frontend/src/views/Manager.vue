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
      <DialogField
        v-model:show="show"
        :title="dialogConfig.title"
        :label="dialogConfig.label"
        :placeholder="dialogConfig.placeholder"
        @confirm="onDialogConfirm"
      />
    </div>
    <van-popup
      v-model:show="showpopup"
      position="bottom"
    >
      <div class="container">
        <h3>布局管理</h3>
        <p>这里是布局管理的内容，可以根据需要进行布局设置。</p>
      </div>
      <van-button
        plain
        type="primary"
        @click="onAddZone"
        >添加分区</van-button
      >
      <van-button
        type="primary"
        @click="showpopup = false"
        >关闭</van-button
      >
    </van-popup>
  </div>
</template>
<script setup lang="ts">
import DialogField from '@/components/DialogField.vue'
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { getAllSpaces, addSpace, deleteSpaceById, addArea, getAreasBySpace } from '@/api/manager.ts'
import { showDialog } from 'vant'
const isMobile = ref(false)
const show = ref(false)
const showActions = ref(false)
const spaceName = ref('')
const showpopup = ref(false)
const selectedSpaceId = ref<number | null>(null)
interface Space {
  id: number
  name: string
}
const spaces = ref<Space[]>([])

const actions = [
  { name: '布局管理', color: '#1989fa' },
  { name: '编辑', color: '#1989fa' },
  { name: '删除', color: '#ee0a24' },
]
const onSelect = (action: { name: string }) => {
  console.log('选择了:', action.name, '空间ID:', selectedSpaceId.value)
  if (action.name === '布局管理') {
    // 布局管理逻辑
    getAreasBySpace(selectedSpaceId.value!)
      .then((res) => {
        console.log('获取分区列表成功:', res)
      })
      .catch((err) => {
        console.error('获取分区列表失败:', err)
      })
    showpopup.value = true
  } else if (action.name === '编辑') {
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

const onDialogConfirm = async (value: string) => {
  if (dialogMode.value === 'addSpace') {
    await confirmAddSpace(value)
  } else if (dialogMode.value === 'addZone') {
    await confirmAddZone(value)
  }
  show.value = false
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

const dialogConfig = ref({
  title: '添加空间',
  label: '空间名称',
  placeholder: '请输入空间名称',
})
const dialogMode = ref<'addSpace' | 'addZone' | 'editSpace'>('addSpace')

const onAddSpace = () => {
  dialogMode.value = 'addSpace'
  dialogConfig.value = { title: '添加空间', label: '空间名称', placeholder: '请输入空间名称' }
  show.value = true
}
const onAddZone = () => {
  dialogMode.value = 'addZone'
  dialogConfig.value = { title: '添加分区', label: '分区名称', placeholder: '请输入分区名称' }
  show.value = true
}

async function confirmAddSpace(spaceName: string): Promise<void> {
  try {
    await addSpace(spaceName)
    getAllSpaces().then((res) => {
      spaces.value = res
    })
  } catch (err) {
    console.error('添加空间失败:', err)
  }
}

async function confirmAddZone(zoneName: string): Promise<void> {
  // 这里可以添加调用后端接口的逻辑来添加分区
  console.log('添加分区:', zoneName)
  try {
    if (selectedSpaceId.value !== null) {
      await addArea(null, selectedSpaceId.value, zoneName)
      console.log('添加分区成功:', zoneName)
    } else {
      console.error('未选择空间，无法添加分区')
    }
  } catch (err) {
    console.error('添加分区失败:', err)
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
