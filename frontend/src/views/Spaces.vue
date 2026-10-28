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
      <p>这里是入库新物品的内容，可以根据需要进行操作。</p>
      <!-- 可以使用 CellGroup 作为容器 -->
      <van-cell-group inset>
        <van-field
          v-model="reagentName"
          label="试剂名称 *"
          placeholder="请输入试剂名称"
        />
        <van-field
          v-model="casNumber"
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
          v-model="specification"
          label="规格/包装"
          placeholder="请输入规格/包装"
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
        @click="onAddReagent"
        >提交</van-button
      >
      <van-button
        type="primary"
        @click="showBottom = false"
        >关闭</van-button
      >
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
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import ZoneDisplayNode from '@/components/ZoneDisplayNode.vue'
import ReagentList from '@/components/ReagentList.vue'
import { getZonesBySpace } from '@/api/zone'
import type { Zone } from '@/api/zone'
import { upsertReagent, getReagentsByZone } from '@/api/reagent'
import type { Reagent } from '@/api/reagent'

const spaceId = Number(useRoute().params.id as string) // params.id 是 string | string[] | undefined

const zones = ref<Zone[]>([])
const reagents = ref<Reagent[]>([])
const selectedZoneId = ref<number>(0)
const searchKeyword = ref('')
const showBottom = ref(false)

// 入库表单字段
const reagentName = ref('')
const casNumber = ref('')
const specification = ref('')
// 类别选择：category 存实际值（默认 1 普通试剂），categoryText 是显示文字
// 与后端一致使用数字类型
const category = ref(1)
const categoryText = ref('普通试剂')
const showCategoryPicker = ref(false)
const categoryColumns = [
  { text: '普通试剂', value: 1 },
  { text: '危化品', value: 2 },
  { text: '生物试剂', value: 3 },
  { text: '色谱级试剂', value: 4 },
]
// 有效期：expiryDate 是 van-date-picker 的 v-model（[年, 月, 日] 字符串数组）
// expiryDateText 是显示文字，提交时可直接用 'YYYY-MM-DD' 格式
const expiryDate = ref<string[]>([])
const expiryDateText = ref('')
const showDatePicker = ref(false)
// 不允许选今天之前的日期
const minDate = new Date()

const onCategoryConfirm = ({ selectedOptions }: any) => {
  category.value = selectedOptions[0].value as number
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

const onAddReagent = async () => {
  await upsertReagent({
    zoneId: selectedZoneId.value,
    name: reagentName.value,
    casNumber: casNumber.value,
    category: category.value,
    capacity: null,
    bottleCount: null,
    specification: specification.value,
    expiryDate: expiryDateText.value || null,
  })
  // 提交后清空表单
  reagentName.value = ''
  casNumber.value = ''
  specification.value = ''
  category.value = 1
  categoryText.value = '普通试剂'
  expiryDate.value = []
  expiryDateText.value = ''
  showBottom.value = false
}

watch(selectedZoneId, fetchReagents)

onMounted(async () => {
  zones.value = await getZonesBySpace(spaceId)
})
</script>
