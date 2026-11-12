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
          v-if="currentReagent?.category !== 1"
          plain
          type="primary"
          :disabled="!currentReagent?.openDate"
          @click="openUsageList"
          >使用记录</van-button
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
  <van-popup
    v-model:show="showUsageListPopup"
    position="bottom"
    height="70%"
  >
    <van-list
      v-model:loading="usageLoading"
      :finished="usageFinished"
      finished-text="没有更多了"
      @load="UsageOnLoad"
    >
      <div
        class="usage-row usage-header"
        :class="{ 'usage-row--compact': !showAmountCols }"
      >
        <span>使用人</span>
        <span>使用时间</span>
        <span v-if="showAmountCols">使用量</span>
        <span v-if="showAmountCols">剩余量</span>
      </div>
      <div
        v-for="item in usageList"
        :key="item.id"
        class="usage-row"
        :class="{ 'usage-row--compact': !showAmountCols }"
      >
        <span>{{ item.user_name }}</span>
        <span>{{ item.usage_time.slice(5, 16) }}</span>
        <span v-if="showAmountCols">{{ item.amount != null ? item.amount + 'ml' : '—' }}</span>
        <span v-if="showAmountCols">{{
          item.remaining_after != null ? item.remaining_after + 'ml' : '—'
        }}</span>
      </div>
    </van-list>
  </van-popup>
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
import { getZonesBySpace } from '@/api/zones'
import type { Zone } from '@/api/zones'
import { upsertReagent, getReagentsByZone } from '@/api/reagent'
import type { Reagent, ReagentPayload } from '@/api/reagent'
import { useReagentActions } from '@/composables/useReagentActions'
import { getReagentUsage, type ReagentUsage, type ReagentUsageList } from '@/api/reagentusage'

const spaceId = Number(useRoute().params.id as string)
const zones = ref<Zone[]>([])
const reagents = ref<Reagent[]>([])
const selectedZoneId = ref(-1)
const activePath = ref<number[]>([])
const showUsageListPopup = ref(false)
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
const usageList = ref<ReagentUsage[]>([])
const usagePage = ref(1)
const usageLoading = ref(false)
const usageFinished = ref(false)
const UsageOnLoad = async () => {
  if (!currentReagent.value) return
  usageLoading.value = true
  try {
    const usageListData: ReagentUsageList = await getReagentUsage(
      currentReagent.value.id,
      usagePage.value,
    )
    usageList.value.push(...usageListData.records)
    usagePage.value += 1
    usageFinished.value = usageListData.records.length < 20
  } catch {
    // 请求失败时停止 van-list 继续触发 load，避免 loading 卡死
    usageFinished.value = true
  } finally {
    usageLoading.value = false
  }
}

// van-list 在 van-popup 里 immediate-check 时机不可靠（挂载时弹窗还在滑入动画中），
// 改为打开弹窗时手动加载第一页，同时重置状态避免混入上一个试剂的记录
const openUsageList = () => {
  usageList.value = []
  usagePage.value = 1
  usageFinished.value = false
  showUsageListPopup.value = true
  UsageOnLoad()
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

const showAmountCols = computed(() => currentReagent.value?.category === 4)

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

<style scoped>
.usage-row {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  padding: 10px 16px;
  font-size: 14px;
  border-bottom: 1px solid #ebedf0;
  text-align: center;
  align-items: center;
}

.usage-row--compact {
  grid-template-columns: 1fr 2fr;
}

.usage-header {
  position: sticky;
  top: 0;
  background: #f7f8fa;
  font-weight: 600;
  z-index: 1;
}
</style>
