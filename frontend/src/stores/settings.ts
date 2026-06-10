import { defineStore } from 'pinia'
import { http } from '../api/http'

export type RoiPoint = [number, number]

export interface SettingsResponse {
  conf_thres: number
  iou_thres: number
  retention_days: number
  roi_polygon: RoiPoint[]
}

export const useSettingsStore = defineStore('settings', {
  state: (): {
    conf: number
    iou: number
    retentionDays: number
    roiPolygon: RoiPoint[]
    loaded: boolean
  } => ({
    conf: 0.35,
    iou: 0.45,
    retentionDays: 7,
    roiPolygon: [],
    loaded: false
  }),

  actions: {
    async fetchSettings() {
      const { data } = await http.get<SettingsResponse>('/api/settings')
      this.conf = data.conf_thres
      this.iou = data.iou_thres
      this.retentionDays = data.retention_days
      this.roiPolygon = data.roi_polygon || []
      this.loaded = true
    },

    async saveParams() {
      await http.post('/api/settings', {
        conf_thres: this.conf,
        iou_thres: this.iou,
        retention_days: this.retentionDays
      })
    },

    async saveRoi() {
      await http.post('/api/upload/roi', { points: this.roiPolygon })
    }
  }
})
