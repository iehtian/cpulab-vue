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
          :to="{ name: 'Spaces', params: { id: space.id } }"
        >
          <template #right-icon>
            <van-icon
              name="ellipsis"
              class="more-icon"
              @click.stop="((showSpaceActions = true), (selectedSpaceId = space.id))"
            /> </template
        ></van-cell>
      </van-cell-group>

      <van-action-sheet
        v-model:show="showSpaceActions"
        v-model:id="selectedSpaceId"
        :actions="spaceActions"
        cancel-text="取消"
        close-on-click-action
        @select="onSelect"
      />
      <DialogField
        v-model:show="showInputDialog"
        :title="dialogConfig.title"
        :label="dialogConfig.label"
        :placeholder="dialogConfig.placeholder"
        @confirm="onDialogConfirm"
      />
    </div>
    <van-popup
      v-model:show="showZonePopup"
      position="bottom"
    >
      <div class="container">
        <h3>布局管理</h3>
        <p>这里是布局管理的内容，可以根据需要进行布局设置。</p>
      </div>
      <ZoneManageNode
        v-for="area in areas"
        :key="area.id"
        :area="area"
        @add="onAddZone"
      />
      <van-button
        plain
        type="primary"
        @click="onAddZone"
        >添加分区</van-button
      >
      <van-button
        type="primary"
        @click="showZonePopup = false"
        >关闭</van-button
      >
    </van-popup>
    <DeleteDialog
      v-model:show="showDeleteDialog"
      @confirm="confirmDelete"
    />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DialogField from '@/components/DialogField.vue'
import DeleteDialog from '@/components/DeleteDialog.vue'
import ZoneManageNode from '@/components/ZoneManageNode.vue'
import { getAllSpaces, addSpace, deleteSpaceById } from '@/api/space'
import type { Space } from '@/api/space'
import { addZone, getZonesBySpace } from '@/api/zone'
import type { Zone } from '@/api/zone'

interface DialogOptions {
  title: string
  label: string
  placeholder: string
  initialValue?: string
  onSubmit: (value: string) => Promise<void>
}

const spaceActions = [
  { name: '布局管理', color: '#1989fa' },
  { name: '编辑', color: '#1989fa' },
  { name: '删除', color: '#ee0a24' },
]

const spaces = ref<Space[]>([])
const selectedSpaceId = ref<number | null>(null)
const areas = ref<Zone[]>([])

const showSpaceActions = ref(false)
const showInputDialog = ref(false)
const showDeleteDialog = ref(false)
const showZonePopup = ref(false)
const dialogConfig = ref<DialogOptions>({
  title: '',
  label: '',
  placeholder: '',
  onSubmit: async () => {},
})

const fetchSpaces = async () => {
  try {
    spaces.value = await getAllSpaces()
  } catch (err) {
    console.error('获取空间列表失败:', err)
  }
}

const fetchZones = async (spaceId: number) => {
  try {
    areas.value = await getZonesBySpace(spaceId)
  } catch (err) {
    console.error('获取分区列表失败:', err)
  }
}

function openDialog(options: DialogOptions) {
  dialogConfig.value = options
  showInputDialog.value = true
}

// 唯一入口：DialogField 的 confirm 事件
const onDialogConfirm = async (value: string) => {
  try {
    await dialogConfig.value.onSubmit(value)
  } catch (err) {
    console.error('操作失败:', err)
  } finally {
    showInputDialog.value = false
  }
}

const onSelect = (action: { name: string }) => {
  if (action.name === '布局管理') {
    // 布局管理逻辑
    fetchZones(selectedSpaceId.value!)
    showZonePopup.value = true
  } else if (action.name === '编辑') {
    // 编辑逻辑
  } else if (action.name === '删除') {
    // 删除逻辑
    showDeleteDialog.value = true
  }
}

const onAddSpace = () =>
  openDialog({
    title: '添加空间',
    label: '空间名称',
    placeholder: '请输入空间名称',
    onSubmit: async (name) => {
      await addSpace(name)
      await fetchSpaces()
    },
  })

const onAddZone = (parentId: number | null) =>
  openDialog({
    title: '添加分区',
    label: '分区名称',
    placeholder: '请输入分区名称',
    onSubmit: async (name) => {
      if (selectedSpaceId.value === null) return
      await addZone(parentId, selectedSpaceId.value, name)
      await fetchZones(selectedSpaceId.value)
    },
  })

const confirmDelete = async () => {
  if (selectedSpaceId.value === null) return
  try {
    await deleteSpaceById(selectedSpaceId.value)
    await fetchSpaces()
  } catch (err) {
    console.error('删除空间失败:', err)
  } finally {
    showDeleteDialog.value = false
  }
}

onMounted(fetchSpaces)
</script>

<style scoped>
.van-cell-group--inset {
  margin: 1rem;
}
.container {
  background-color: aliceblue;
  border-radius: 16px;
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
.down2up {
  transform: rotate(180deg);
  font-size: 18px;
  color: #969799;
  padding: 4px;
}
</style>
