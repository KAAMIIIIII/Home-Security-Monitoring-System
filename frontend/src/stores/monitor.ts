import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface FrameAlarm {
  alarm_type: string
  level: string
  message: string
}

interface StickyAlarm extends FrameAlarm {
  expireAt: number
}

interface WsFrameMessage {
  type: 'frame'
  jpeg?: string
  t_capture?: number
  alarms?: FrameAlarm[]
}

interface WsErrorMessage {
  type: 'error'
  message?: string
}

type WsMessage = WsFrameMessage | WsErrorMessage

const ALARM_STICKY_MS = 10 * 60 * 1000
const LATENCY_SMOOTH = 0.22

export const useMonitorStore = defineStore('monitor', () => {
  // -- 连接状态 --
  const running = ref(false)
  const wsStatus = ref('未连接')
  let ws: WebSocket | null = null

  // -- 视频流 --
  const jpeg = ref('')
  const jpegSrc = computed(() => {
    if (!jpeg.value) return ''
    return `data:image/jpeg;base64,${jpeg.value}`
  })

  // -- FPS / 延迟统计 --
  const statsFps = ref(0)
  const statsLatencyMs = ref<number | null>(null)
  let framesInSecond = 0
  let latencyEma: number | null = null
  let pendingE2eCaptureSec: number | null = null
  let statsTimer: ReturnType<typeof setInterval> | null = null

  const latencyLabel = computed(() => {
    const v = statsLatencyMs.value
    if (v == null || !Number.isFinite(v)) return '--'
    return `${Math.round(v)} ms`
  })

  // -- 告警 --
  const stickyAlarms = ref<StickyAlarm[]>([])
  const alarmClock = ref(0)
  let pruneTimer: ReturnType<typeof setInterval> | null = null

  const alarms = computed(() => {
    alarmClock.value
    const now = Date.now()
    return stickyAlarms.value
      .filter((a) => a.expireAt > now)
      .sort((a, b) => b.expireAt - a.expireAt)
      .slice(0, 5)
      .map(({ alarm_type, level, message }) => ({ alarm_type, level, message }))
  })

  // -- 内部辅助 --
  function resetStreamStats() {
    statsFps.value = 0
    statsLatencyMs.value = null
    framesInSecond = 0
    latencyEma = null
    pendingE2eCaptureSec = null
  }

  function tickStreamStats() {
    statsFps.value = framesInSecond
    framesInSecond = 0
  }

  function recordFrameReceived() {
    framesInSecond++
  }

  function onStreamFrameDecoded() {
    const cap = pendingE2eCaptureSec
    if (typeof cap !== 'number' || !Number.isFinite(cap)) return
    const ms = Date.now() - cap * 1000
    const clamped = Math.max(0, Math.min(ms, 120_000))
    latencyEma = latencyEma == null ? clamped : LATENCY_SMOOTH * clamped + (1 - LATENCY_SMOOTH) * latencyEma
    statsLatencyMs.value = latencyEma
  }

  function alarmKey(a: FrameAlarm): string {
    return `${a.alarm_type}\0${a.message}`
  }

  function ingestFrameAlarms(incoming: FrameAlarm[]) {
    const now = Date.now()
    const map = new Map<string, StickyAlarm>()
    for (const a of stickyAlarms.value) {
      if (a.expireAt > now) map.set(alarmKey(a), { ...a })
    }
    for (const a of incoming || []) {
      map.set(alarmKey(a), {
        alarm_type: a.alarm_type,
        level: a.level,
        message: a.message,
        expireAt: now + ALARM_STICKY_MS
      })
    }
    stickyAlarms.value = [...map.values()]
      .sort((a, b) => b.expireAt - a.expireAt)
      .slice(0, 20)
  }

  function pruneExpiredAlarms() {
    alarmClock.value++
    const now = Date.now()
    const next = stickyAlarms.value.filter((a) => a.expireAt > now)
    if (next.length !== stickyAlarms.value.length) {
      stickyAlarms.value = next
    }
  }

  // -- 公开动作 --
  function start() {
    if (running.value) return
    running.value = true
    stickyAlarms.value = []
    jpeg.value = ''
    resetStreamStats()

    if (pruneTimer) clearInterval(pruneTimer)
    pruneTimer = setInterval(pruneExpiredAlarms, 1000)
    if (statsTimer) clearInterval(statsTimer)
    statsTimer = setInterval(tickStreamStats, 1000)

    wsStatus.value = '连接中...'
    ws = new WebSocket('ws://127.0.0.1:8000/api/video/stream')

    ws.onopen = () => {
      wsStatus.value = '已连接'
      ws!.send(JSON.stringify({ type: 'start' }))
    }

    ws.onmessage = (ev: MessageEvent) => {
      try {
        const msg: WsMessage = JSON.parse(ev.data as string)
        if (msg.type === 'error') {
          stop()
          return
        }
        if (msg.type === 'frame') {
          const cap = msg.t_capture
          if (typeof cap === 'number' && Number.isFinite(cap)) {
            pendingE2eCaptureSec = cap
          } else {
            pendingE2eCaptureSec = null
            latencyEma = null
            statsLatencyMs.value = null
          }
          jpeg.value = msg.jpeg || ''
          ingestFrameAlarms(msg.alarms || [])
          recordFrameReceived()
        }
      } catch (_e) {
        // 忽略解析失败
      }
    }

    ws.onclose = () => {
      wsStatus.value = '已断开'
      running.value = false
    }

    ws.onerror = () => {
      wsStatus.value = '连接失败'
      running.value = false
    }
  }

  function stop() {
    running.value = false
    wsStatus.value = '已断开'
    if (pruneTimer) {
      clearInterval(pruneTimer)
      pruneTimer = null
    }
    if (statsTimer) {
      clearInterval(statsTimer)
      statsTimer = null
    }
    resetStreamStats()
    stickyAlarms.value = []
    if (ws) {
      try {
        ws.close()
      } catch (_e) {}
    }
    ws = null
  }

  return {
    running,
    wsStatus,
    jpeg,
    jpegSrc,
    statsFps,
    statsLatencyMs,
    latencyLabel,
    alarms,
    start,
    stop,
    onStreamFrameDecoded
  }
})
