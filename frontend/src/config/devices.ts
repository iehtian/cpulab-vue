export interface DeviceInfo {
  id: string
  name: string
  description: string
  enabled: boolean
  totalSlots: number
  hasDuty: boolean
}

export const DEVICES: DeviceInfo[] = [
  {
    id: 'CellRoom',
    name: '细胞房',
    description: '细胞房',
    enabled: true,
    totalSlots: 32,
    hasDuty: true,
  },
  {
    id: 'HPLC',
    name: '高效液相色谱分析仪',
    description: '高效液相色谱分析仪',
    enabled: true,
    totalSlots: 16,
    hasDuty: false,
  },
]

export function getDeviceById(id: string): DeviceInfo | undefined {
  return DEVICES.find((d) => d.id === id)
}
