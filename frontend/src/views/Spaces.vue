<template>
  <div>
    <ZoneDisplayNode
      :zones="zones"
      :depth="0"
      :path="activePath"
      @selected="selectedDisplay"
    />
    <ReagentList
      :reagents="reagents"
      @select="openDetailById"
    />
    <ReagentDetailActions
      v-model:show="showDetailPopup"
      :reagent="currentReagent"
      show-edit
      show-delete
      @refresh="fetchReagents"
      @edit="onReagentEdit"
    />
  </div>
  <van-submit-bar
    v-if="selectedZoneId !== -1"
    style="bottom: 50px"
    button-text="入库新物品"
    button-color="#1989fa"
    :loading="false"
    @submit="showFormPopup = true"
  />
  <van-popup
    v-model:show="showFormPopup"
    position="bottom"
  >
    <div class="container">
      <van-form
        ref="formRef"
        @submit="onSubmit"
        @failed="onFailed"
      >
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            name="name"
            label="试剂名称"
            placeholder="请输入试剂名称"
            required
            :rules="[{ required: true, message: '请输入试剂名称' }]"
          />
          <van-field
            v-model="form.casNumber"
            name="casNumber"
            label="CAS号"
            placeholder="请输入CAS号"
          />
          <van-field
            v-model="categoryText"
            is-link
            readonly
            label="类别"
            placeholder="请选择类别"
            @click="openCategoryPicker"
          />
          <van-field
            v-if="form.category === ReagentCategory.CHROMATOGRAPHY"
            v-model="form.capacity"
            name="capacity"
            label="单瓶容量"
            placeholder="请输入容量"
            required
            type="digit"
            :rules="[{ validator: validatePositive, message: '容量必须大于0' }]"
          />
          <van-field
            v-if="form.category === ReagentCategory.CHROMATOGRAPHY"
            v-model="form.bottleCount"
            name="bottleCount"
            label="瓶数"
            placeholder="请输入瓶数"
            required
            type="digit"
            :rules="[{ validator: validatePositive, message: '瓶数必须大于0' }]"
          />
        </van-cell-group>
        <div class="action-buttons">
          <van-button
            type="primary"
            native-type="submit"
            >提交</van-button
          >
          <van-button
            type="primary"
            @click="showFormPopup = false"
            >关闭</van-button
          >
        </div>
      </van-form>
    </div>
  </van-popup>
  <van-popup
    v-model:show="showCategoryPicker"
    position="bottom"
  >
    <van-picker
      v-model="categoryPickerValue"
      :columns="categoryColumns"
      @confirm="onCategoryConfirm"
      @cancel="showCategoryPicker = false"
    />
  </van-popup>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { showToast } from 'vant'
import ZoneDisplayNode from '@/components/ZoneDisplayNode.vue'
import ReagentList from '@/components/ReagentList.vue'
import ReagentDetailActions from '@/components/ReagentDetailActions.vue'
import { categoryColumns, ReagentCategory } from '@/constants/reagent'
import { getZonesBySpace } from '@/api/zones'
import type { Zone } from '@/api/zones'
import { upsertReagent, getReagentsByZone } from '@/api/reagent'
import type { Reagent, ReagentPayload } from '@/api/reagent'

import { useUserStore } from '@/stores/user'

const spaceId = Number(useRoute().params.id as string)
const userStore = useUserStore()
const zones = ref<Zone[]>([])
const reagents = ref<Reagent[]>([])
const selectedZoneId = ref(-1)
const activePath = ref<number[]>([])

const showFormPopup = ref(false)
const initialForm = () => ({
  name: '',
  casNumber: '',
  category: ReagentCategory.NORMAL as ReagentCategory,
  capacity: '',
  bottleCount: '',
})
const form = reactive(initialForm())
// 显示文本直接派生自 form.category，新增/编辑/重置三条路径都不用单独维护
const categoryText = computed(
  () => categoryColumns.find((c) => c.value === form.category)?.text ?? '普通试剂',
)
const showCategoryPicker = ref(false)
// 滚动过程只改中间变量，点取消丢弃、点确认才写入 form.category
const categoryPickerValue = ref<number[]>([])

const openCategoryPicker = () => {
  categoryPickerValue.value = [form.category] // 打开时定位到当前类别
  showCategoryPicker.value = true
}

const onCategoryConfirm = ({ selectedValues }: any) => {
  form.category = selectedValues[0] as ReagentCategory
  showCategoryPicker.value = false
}

const fetchReagents = async () => {
  reagents.value = await getReagentsByZone(selectedZoneId.value)
}

const showDetailPopup = ref(false)
const currentReagentId = ref(-1)

const currentReagent = computed(
  () => reagents.value.find((r) => r.id === currentReagentId.value) ?? undefined,
)

const openDetailById = (id: number) => {
  currentReagentId.value = id
  showDetailPopup.value = true
}

const validatePositive = (val: string) => val !== '' && Number(val) > 0

// 校验全部通过后触发，values 是 van-form 按各 field 的 name 聚合出的对象
const onSubmit = async (values: Record<string, string>) => {
  if (userStore.userId === null) {
    showToast('请先登录')
    return
  }
  // 项目开了 noUncheckedIndexedAccess，索引取值带 undefined，这里解构给默认值
  const { name = '', casNumber = '', capacity = '', bottleCount = '' } = values
  const payload: ReagentPayload = {
    zoneId: selectedZoneId.value,
    name,
    casNumber,
    category: form.category,
    capacity: capacity ? Number(capacity) : null,
    bottleCount: bottleCount ? Number(bottleCount) : null,
  }
  await upsertReagent(payload, userStore.userId)
  await fetchReagents()
  // 提交后重置表单（form.category 回到 1 后 categoryText 自动跟随）
  Object.assign(form, initialForm())
  showFormPopup.value = false
}

const onFailed = (errorInfo: { errors: { message?: string }[] }) => {
  showToast(errorInfo.errors[0]?.message ?? '请检查后填写')
}

const onReagentEdit = () => {
  const reagent = currentReagent.value
  if (!reagent) return
  form.name = reagent.name
  form.casNumber = reagent.casNumber
  form.category = reagent.category
  form.capacity = reagent.capacity != null ? String(reagent.capacity) : ''
  form.bottleCount = reagent.bottleCount != null ? String(reagent.bottleCount) : ''
  showFormPopup.value = true
}

// 沿 activePath 逐层下钻，把 selectedZoneId 定位到当前路径对应的 zone；路径不足的层默认选第一项
const resolveSelectedZone = (zones: Zone[], path: number[], depth: number) => {
  if (zones.length === 0) return
  if (depth >= path.length) path.push(0)
  const zone = zones.at(path.at(depth) ?? 0)
  if (!zone) return
  selectedZoneId.value = zone.id
  if (zone.children?.length) {
    resolveSelectedZone(zone.children, path, depth + 1)
  }
}

watch(selectedZoneId, fetchReagents)

const selectedDisplay = ({ depth, index }: { depth: number; index: number }) => {
  activePath.value = activePath.value.slice(0, depth)
  activePath.value[depth] = index
  resolveSelectedZone(zones.value, activePath.value, 0)
}

onMounted(async () => {
  zones.value = await getZonesBySpace(spaceId)
  resolveSelectedZone(zones.value, activePath.value, 0)
})
</script>

<style scoped></style>
