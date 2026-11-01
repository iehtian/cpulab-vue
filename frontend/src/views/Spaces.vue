<template>
  <div>
    <van-search
      v-model="searchKeyword"
      placeholder="请输入搜索关键词"
    />
    <ZoneDisplayNode
      v-model:zone-id="selectedZoneId"
      :zones="zones"
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
      <h3>入库新物品</h3>
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
          <van-field
            v-model="expiryDateText"
            is-link
            readonly
            label="有效期至"
            placeholder="请选择有效期"
            @click="showDatePicker = true"
          />
        </van-cell-group>

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
  <van-popup
    v-model:show="showDatePicker"
    position="bottom"
  >
    <van-date-picker
      v-model="expiryDate"
      title="选择有效期"
      :min-date="minDate"
      @confirm="onDateConfirm"
      @cancel="showDatePicker = false"
    />
  </van-popup>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive } from 'vue'
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
const expiryDate = ref<string[]>([])
const expiryDateText = ref('')

const showCategoryPicker = ref(false)
const showDatePicker = ref(false)

// 不允许选今天之前的日期
const minDate = new Date()

const onCategoryConfirm = ({ selectedOptions }: any) => {
  form.category = selectedOptions[0].value as number
  categoryText.value = selectedOptions[0].text as string
  showCategoryPicker.value = false
}

const onDateConfirm = () => {
  expiryDateText.value = expiryDate.value.join('-')
  showDatePicker.value = false
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
    expiryDate: expiryDateText.value,
  }
  await upsertReagent(payload)
  fetchReagents()
  // 提交后重置表单
  Object.assign(form, initialForm())
  categoryText.value = '普通试剂'
  expiryDate.value = []
  expiryDateText.value = ''
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
  expiryDateText.value = reagent.expiryDate ?? ''
  showBottom.value = true
}

watch(selectedZoneId, fetchReagents)

onMounted(async () => {
  zones.value = await getZonesBySpace(spaceId)
})
</script>
