<template>
  <div>
    <van-search
      v-model="searchKeyword"
      placeholder="请输入搜索关键词"
    />
    <ZoneDisplayNode
      v-model:zoneid="selectedZoneId"
      :zones="zones"
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ZoneDisplayNode from '@/components/ZoneDisplayNode.vue'
const id = Number(useRoute().params.id as string) // params.id 是 string | string[] | undefined
import { getZonesBySpace, upsertReagent, getReagentsByZone } from '@/api/manager.ts'
import type { Zone } from '@/api/manager.ts'
const zones = ref<Zone[]>([])
const searchKeyword = ref('')
const showBottom = ref(false)
const selectedZoneId = ref<number>(0)
// 入库表单字段
const reagentName = ref('')
const casNumber = ref('')
const specification = ref('')
// 类别选择：category 存实际值（默认 '1' 普通试剂），categoryText 是显示文字
const category = ref('1')
const categoryText = ref('普通试剂')
const showCategoryPicker = ref(false)
const categoryColumns = [
  { text: '普通试剂', value: '1' },
  { text: '危化品', value: '2' },
  { text: '生物试剂', value: '3' },
  { text: '色谱级试剂', value: '4' },
]
const onCategoryConfirm = ({ selectedOptions }: any) => {
  category.value = selectedOptions[0].value as string
  categoryText.value = selectedOptions[0].text as string
  showCategoryPicker.value = false
}
// 有效期：expiryDate 是 van-date-picker 的 v-model（[年, 月, 日] 字符串数组）
// expiryDateText 是显示文字，提交时可直接用 'YYYY-MM-DD' 格式
const expiryDate = ref<string[]>([])
const expiryDateText = ref('')
const showDatePicker = ref(false)
// 不允许选今天之前的日期
const minDate = new Date()

const onDateConfirm = () => {
  expiryDateText.value = expiryDate.value.join('-')
  showDatePicker.value = false
}

const onAddReagent = () => {
  // 这里可以调用 API 提交入库信息
  console.log('提交入库信息:', {
    reagentName: reagentName.value,
    casNumber: casNumber.value,
    specification: specification.value,
    category: category.value,
    expiryDate: expiryDateText.value,
  })
  upsertReagent(
    selectedZoneId.value,
    reagentName.value,
    casNumber.value,
    category.value,
    null,
    null,
    specification.value,
    expiryDateText.value || null,
  )
  // 提交后清空表单
  reagentName.value = ''
  casNumber.value = ''
  specification.value = ''
  category.value = '1'
  categoryText.value = '普通试剂'
  expiryDate.value = []
  expiryDateText.value = ''
  showBottom.value = false
}
onMounted(() => {
  getZonesBySpace(id).then((res) => {
    console.log('获取分区数据:', res)
    zones.value = res
  })
})
</script>
