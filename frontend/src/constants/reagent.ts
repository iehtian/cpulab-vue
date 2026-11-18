export const CATEGORY_MAP: Record<
  number,
  { text: string; type: 'primary' | 'danger' | 'warning' | 'success' }
> = {
  1: { text: '普通试剂', type: 'primary' },
  2: { text: '危化品', type: 'danger' },
  3: { text: '生物试剂', type: 'warning' },
  4: { text: '色谱级试剂', type: 'success' },
}

export const categoryColumns = Object.entries(CATEGORY_MAP).map(([value, { text }]) => ({
  text,
  value: Number(value),
}))
