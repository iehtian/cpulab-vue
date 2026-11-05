<template>
  <div>
    <van-search
      v-model="searchKeyword"
      placeholder="请输入搜索关键词"
    />
    <ZoneDisplayNode
      :zones="zones"
      :depth="0"
      :path="activePath"
      @selected="selectedDisplay"
    />
    <ReagentList
      :reagents="reagents"
      @update-reagents="fetchReagents"
      @edit-reagent="onReagentEdit"
    />
  </div>
  <van-submit-bar
    style="bottom: 50px"
    button-text="入库新物品"
    button-color="#1989fa"
    :loading="false"
    @submit="showBottom = true"
  />
  <van-popup
    v-model:show="showBottom"
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
            @click="showCategoryPicker = true"
          />
          <van-field
            v-model="form.specification"
            name="specification"
            label="规格/包装"
            placeholder="请输入规格/包装"
          />
          <van-field
            v-if="form.category === 4"
            v-model="form.capacity"
            name="capacity"
            label="单瓶容量"
            placeholder="请输入容量"
            required
            type="digit"
            :rules="[{ validator: validatePositive, message: '容量必须大于0' }]"
          />
          <van-field
            v-if="form.category === 4"
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
            @click="showBottom = false"
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
import { categoryColumns } from '@/constants/reagent'
import { getZonesBySpace } from '@/api/zone'
import type { Zone } from '@/api/zone'
import { upsertReagent, getReagentsByZone } from '@/api/reagent'
import type { Reagent, ReagentPayload } from '@/api/reagent'

const spaceId = Number(useRoute().params.id as string) // params.id 是 string | string[] | undefined

const zones = ref<Zone[]>([])
const reagents = ref<Reagent[]>([])
const selectedZoneId = ref<number>(0)
const searchKeyword = ref('')
const showBottom = ref(false)
const activePath = ref<number[]>([])
const initialForm = () => ({
  name: '',
  casNumber: '',
  category: 1,
  specification: '',
  capacity: '',
  bottleCount: '',
})
const form = reactive(initialForm())
const categoryText = ref('普通试剂')
const showCategoryPicker = ref(false)

const onCategoryConfirm = ({ selectedOptions }: any) => {
  form.category = selectedOptions[0].value as number
  categoryText.value = selectedOptions[0].text as string
  showCategoryPicker.value = false
}

const fetchReagents = async () => {
  reagents.value = await getReagentsByZone(selectedZoneId.value)
}

// 容量/瓶数：必填且大于 0
const validatePositive = (val: string) => val !== '' && Number(val) > 0

// 校验全部通过后触发，values 是 van-form 按各 field 的 name 聚合出的对象
const onSubmit = async (values: Record<string, string>) => {
  // 项目开了 noUncheckedIndexedAccess，索引取值带 undefined，这里解构给默认值
  const { name = '', casNumber = '', specification = '', capacity = '', bottleCount = '' } = values
  const payload: ReagentPayload = {
    zoneId: selectedZoneId.value,
    name,
    casNumber,
    category: form.category,
    capacity: capacity ? Number(capacity) : null,
    bottleCount: bottleCount ? Number(bottleCount) : null,
    specification: specification,
  }
  await upsertReagent(payload)
  fetchReagents()
  // 提交后重置表单
  Object.assign(form, initialForm())
  categoryText.value = '普通试剂'
  showBottom.value = false
}

const onFailed = (errorInfo: { errors: { message?: string }[] }) => {
  showToast(errorInfo.errors[0]?.message ?? '请检查后填写')
}

const onReagentEdit = (reagent: Reagent) => {
  console.log('onReagentUsed', reagent)
  form.bottleCount = String(reagent.bottleCount)
  form.capacity = String(reagent.capacity)
  form.category = reagent.category
  form.name = reagent.name
  form.specification = reagent.specification
  form.casNumber = reagent.casNumber
  showBottom.value = true
}

const activePathLength = computed(() => activePath.value.length)

function tt(zones: Zone[], path: number[], depth: number) {
  if (zones.length === 0) return
  if (depth >= activePathLength.value) {
    path.push(0)
  }
  const index = path.at(depth) ?? 0
  const zone = zones.at(index)
  if (!zone) return
  selectedZoneId.value = zone.id
  if (zone && zone.children?.length) {
    tt(zone.children, path, depth + 1)
  }
}

watch(selectedZoneId, fetchReagents)
const selectedDisplay = ({ depth, index }: { depth: number; index: number }) => {
  activePath.value = activePath.value.slice(0, depth)
  activePath.value[depth] = index
  tt(zones.value, activePath.value, 0)
}

onMounted(async () => {
  zones.value = await getZonesBySpace(spaceId)
  tt(zones.value, activePath.value, 0)
})
</script>
