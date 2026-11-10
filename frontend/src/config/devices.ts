import type { Component } from 'vue'
import { Virus , TestTubes } from '@lucide/vue'
export interface DeviceInfo {
  id: string
  name: string
  icon: Component
  description: string
  enabled: boolean
  totalSlots: number
}

export const DEVICES: DeviceInfo[] = [
  {
    id: 'CellRoom',
    name: '细胞房',
    icon: Virus,
    description: '细胞房',
    enabled: true,
    totalSlots: 32,
  },
  {
    id: 'HPLC',
    name: '高效液相色谱仪',
    icon: TestTubes,
    description: '高效液相色谱分析仪',
    enabled: true,
    totalSlots: 32,
  },
]

export function getDeviceById(id: string): DeviceInfo | undefined {
  return DEVICES.find((d) => d.id === id)
}
