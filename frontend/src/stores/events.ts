import { defineStore } from 'pinia'
import { http } from '../api/http'
import { parseToBeijingDate, isSameDay } from '../utils/date'

export interface SecurityEvent {
  id: number
  created_at: string
  alarm_type: string
  image_path: string
  image_url?: string
}

export const useEventsStore = defineStore('events', {
  state: (): { events: SecurityEvent[] } => ({
    events: []
  }),

  getters: {
    todayCount: (state): number => {
      const now = new Date()
      return state.events.filter((e) => isSameDay(parseToBeijingDate(e.created_at), now)).length
    },
    totalCount: (state): number => state.events.length
  },

  actions: {
    async fetchEvents() {
      const { data } = await http.get<SecurityEvent[]>('/api/events')
      this.events = data
    },

    async deleteEvent(id: number) {
      await http.delete(`/api/events/${id}`)
      this.events = this.events.filter((e) => e.id !== id)
    },

    async batchDeleteEvents(ids: number[]) {
      await http.delete('/api/events/batch', { data: { ids } })
      const idSet = new Set(ids)
      this.events = this.events.filter((e) => !idSet.has(e.id))
    }
  }
})
