export interface DeviceInfo {
  id: string
  name: string
  description: string
  enabled: boolean
  totalSlots: number // 轴长：slot 0 = 00:00，每格 step = 1440 / totalSlots 分钟
  visibleFrom: number // 可见起始 slot id（含）
  visibleTo: number // 可见结束 slot id（不含）
  hasDuty: boolean
}

export const DEVICES: DeviceInfo[] = [
  {
    id: 'CellRoom',
    name: '细胞房',
    description: '细胞房',
    enabled: true,
    totalSlots: 48,
    visibleFrom: 12,
    visibleTo: 48,
    hasDuty: true,
  },
  {
    id: 'Agilent',
    name: '安捷伦液相预约',
    description: '高效液相色谱分析仪',
    enabled: true,
    totalSlots: 24,
    visibleFrom: 0,
    visibleTo: 24,
    hasDuty: false,
  },
  {
    id: 'Shimadzu',
    name: '岛津液相预约',
    description: '高效液相色谱分析仪',
    enabled: true,
    totalSlots: 24,
    visibleFrom: 0,
    visibleTo: 24,
    hasDuty: false,
  },
]

export function getDeviceById(id: string): DeviceInfo | undefined {
  return DEVICES.find((d) => d.id === id)
}
