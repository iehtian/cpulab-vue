export interface DeviceInfo {
  id: string
  name: string
  description: string
  enabled: boolean
  daystarthour: number
  totalSlots: number
  hasDuty: boolean
}

export const DEVICES: DeviceInfo[] = [
  {
    id: 'CellRoom',
    name: '细胞房',
    description: '细胞房',
    enabled: true,
    daystarthour: 6,
    totalSlots: 36,
    hasDuty: true,
  },
  {
    id: 'HPLC',
    name: '高效液相色谱分析仪',
    description: '高效液相色谱分析仪',
    enabled: true,
    daystarthour: 0,
    totalSlots: 24,
    hasDuty: false,
  },
]

export function getDeviceById(id: string): DeviceInfo | undefined {
  return DEVICES.find((d) => d.id === id)
}
