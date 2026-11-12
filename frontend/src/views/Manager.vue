<template>
  <div>
    <van-grid
      column-num="2"
      clickable
    >
      <van-grid-item
        text="常用试剂"
        to="/common-used"
      >
        <template #icon> <FlaskConical /> </template>
      </van-grid-item>

      <van-grid-item
        text="需补货"
        :badge="need2RestockReagentsLength"
        to="/restock"
      >
        <template #icon> <PackagePlus /> </template>
      </van-grid-item>
    </van-grid>

    <div class="container space">
      <van-cell-group>
        <van-cell title="空间管理">
          <template #value>
            <div
              class="add-space"
              @click="onAddSpace"
            >
              添加空间
            </div>
          </template>
        </van-cell>
        <van-skeleton
          title
          :row="2"
          :loading="spacesLoading"
        >
          <van-cell
            v-for="space in spaces"
            :key="space.id"
            :title="space.name"
            :to="{ name: 'Spaces', params: { id: space.id } }"
          >
            <template #right-icon>
              <van-icon
                name="ellipsis"
                class="more-icon"
                @click.stop="((showSpaceActions = true), (selectedSpaceId = space.id))"
              /> </template
          ></van-cell>
        </van-skeleton>
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
      <ZoneManageNode
        v-for="area in areas"
        :key="area.id"
        :area="area"
        @add="onAddZone"
      />
      <div class="action-buttons">
        <van-button
          plain
          type="primary"
          @click="onAddZone(null)"
          >添加分区</van-button
        >
        <van-button
          type="primary"
          @click="showZonePopup = false"
          >关闭</van-button
        >
      </div>
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
import { FlaskConical, PackagePlus } from '@lucide/vue'
import { getNeed2RestockReagents } from '@/api/reagent'
import { getReagentsByZone } from '@/api/reagent'
import { showSuccessToast } from 'vant'

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

const spacesLoading = ref(false)

const fetchSpaces = async () => {
  spacesLoading.value = true
  try {
    spaces.value = await getAllSpaces()
  } catch (err) {
    console.error('获取空间列表失败:', err)
  } finally {
    spacesLoading.value = false
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
      showSuccessToast({
        message: '空间添加成功，添加分区后才能入库物品',
        duration: 3000, // 默认 2000ms，文案偏长可适当延长
      })
    },
  })

const onAddZone = async (parentId: number | null) => {
  if (selectedSpaceId.value === null) return
  const Id = selectedSpaceId.value
  if (parentId !== null) {
    const reagents = await getReagentsByZone(parentId)
    if (reagents.length > 0) {
      alert('该分区下有试剂，无法添加子分区')
      return
    }
  }
  openDialog({
    title: '添加分区',
    label: '分区名称',
    placeholder: '请输入分区名称',
    onSubmit: async (name) => {
      await addZone(parentId, Id, name)
      await fetchZones(Id)
    },
  })
}

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

import type { Reagent } from '@/api/reagent'
import { computed } from 'vue'
const need2RestockReagents = ref<Reagent[]>([])

const need2RestockReagentsLength = computed(() => need2RestockReagents.value.length)

const fetchNeed2RestockReagents = async () => {
  try {
    const reagents = await getNeed2RestockReagents()
    need2RestockReagents.value = reagents
    console.log('需要补货的试剂:', reagents)
  } catch (err) {
    console.error('获取需要补货的试剂失败:', err)
  }
}

onMounted(() => {
  fetchSpaces()
  fetchNeed2RestockReagents()
})
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
.add-space {
  color: #1989fa;
  cursor: pointer;
}
</style>
