/** 试剂类别枚举（值与后端约定，不要随意改动） */
export enum ReagentCategory {
  NORMAL = 1, // 普通试剂
  HAZARDOUS = 2, // 危化品
  BIOLOGICAL = 3, // 生物试剂
  CHROMATOGRAPHY = 4, // 色谱级试剂
}

export const CATEGORY_MAP: Record<
  ReagentCategory,
  { text: string; type: 'primary' | 'danger' | 'warning' | 'success' }
> = {
  [ReagentCategory.NORMAL]: { text: '普通', type: 'primary' },
  [ReagentCategory.HAZARDOUS]: { text: '危化品', type: 'danger' },
  [ReagentCategory.BIOLOGICAL]: { text: '生物', type: 'warning' },
  [ReagentCategory.CHROMATOGRAPHY]: { text: '色谱级', type: 'success' },
}

export const categoryColumns = Object.entries(CATEGORY_MAP).map(([value, { text }]) => ({
  text,
  value: Number(value),
}))

/** 按次计数的类别（危化品/生物试剂）：取用时不录入用量，只累计次数 */
export const COUNT_BASED_CATEGORIES = new Set<ReagentCategory>([
  ReagentCategory.HAZARDOUS,
  ReagentCategory.BIOLOGICAL,
])
