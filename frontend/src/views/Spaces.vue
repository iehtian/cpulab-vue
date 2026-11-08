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
    <ReagentDetailPopup
      v-model:show="showDetailPopup"
      :currentReagent="currentReagent"
    >
      <template #action-buttons>
        <van-button
          v-if="currentReagent?.category !== 1"
          type="primary"
          :disabled="!currentReagent?.openDate"
          @click="currentReagent && requestUse(currentReagent)"
        >
          取用
        </van-button>
        <van-button
          type="danger"
          @click="currentReagent && requestRestock(currentReagent.id, !currentReagent.need2restock)"
        >
          {{ currentReagent?.need2restock ? '完成补货' : '需要补货' }}
        </van-button>
        <van-button
          v-if="!currentReagent?.openDate"
          plain
          type="primary"
          @click="openReagent"
          >开瓶贴标</van-button
        >
        <van-button
          v-if="!currentReagent?.openDate"
          type="danger"
          @click="onReagentEdit"
          >编辑</van-button
        >
        <van-button
          type="danger"
          @click="requestDelete"
          >删除</van-button
        >
      </template>
    </ReagentDetailPopup>
  </div>
  <van-submit-bar
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
      :columns="categoryColumns"
      @confirm="onCategoryConfirm"
      @cancel="showCategoryPicker = false"
    />
  </van-popup>
  <ReagentUsePopup
    v-model:show="showUsagePopup"
    @confirm="confirmUsage"
  />
  <DeleteDialog
    v-model:visible="showDeleteDialog"
    @confirm="confirmDelete"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { showToast } from 'vant'
import ZoneDisplayNode from '@/components/ZoneDisplayNode.vue'
import ReagentList from '@/components/ReagentList.vue'
import ReagentDetailPopup from '@/components/ReagentDetailPopup.vue'
import ReagentUsePopup from '@/components/ReagentUsePopup.vue'
import DeleteDialog from '@/components/DeleteDialog.vue'
import { categoryColumns } from '@/constants/reagent'
import { getZonesBySpace } from '@/api/zone'
import type { Zone } from '@/api/zone'
import { upsertReagent, getReagentsByZone } from '@/api/reagent'
import type { Reagent, ReagentPayload } from '@/api/reagent'
import { useReagentActions } from '@/composables/useReagentActions'

const spaceId = Number(useRoute().params.id as string) // params.id 是 string | string[] | undefined

const zones = ref<Zone[]>([])
const reagents = ref<Reagent[]>([])
const selectedZoneId = ref(0)
const activePath = ref<number[]>([])

const showFormPopup = ref(false)
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

const {
  showDetailPopup,
  currentReagentId,
  openDetail,
  showUsagePopup,
  requestUse,
  confirmUsage,
  showDeleteDialog,
  requestDelete,
  confirmDelete,
  openReagent,
  requestRestock,
} = useReagentActions(fetchReagents)

const currentReagent = computed(
  () => reagents.value.find((r) => r.id === currentReagentId.value) ?? undefined,
)

const openDetailById = (id: number) => {
  const reagent = reagents.value.find((r) => r.id === id)
  if (reagent) openDetail(reagent)
}

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
    specification,
    capacity: capacity ? Number(capacity) : null,
    bottleCount: bottleCount ? Number(bottleCount) : null,
  }
  await upsertReagent(payload)
  await fetchReagents()
  // 提交后重置表单
  Object.assign(form, initialForm())
  categoryText.value = '普通试剂'
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
  form.specification = reagent.specification
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
