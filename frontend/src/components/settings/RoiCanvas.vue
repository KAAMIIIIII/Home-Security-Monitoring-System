<template>
  <div class="canvas-wrap">
    <canvas
      ref="canvasRef"
      class="roi"
      width="640"
      height="360"
      @click="onCanvasClick"
    />
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'

export type RoiPoint = [number, number]

const props = defineProps<{
  points: RoiPoint[]
}>()

const emit = defineEmits<{
  'update:points': [points: RoiPoint[]]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  const w = canvas.width
  const h = canvas.height

  ctx.clearRect(0, 0, w, h)

  /* 背景 */
  ctx.fillStyle = '#080b10'
  ctx.fillRect(0, 0, w, h)

  /* 网格 */
  ctx.strokeStyle = 'rgba(255,255,255,0.025)'
  ctx.lineWidth = 0.5
  for (let x = 0; x <= w; x += 32) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, h)
    ctx.stroke()
  }
  for (let y = 0; y <= h; y += 32) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(w, y)
    ctx.stroke()
  }

  const pts = props.points.map(([x, y]) => [x * w, y * h] as [number, number])

  /* 边线（未闭合时） */
  if (pts.length >= 2) {
    ctx.strokeStyle = 'rgba(212, 153, 60, 0.5)'
    ctx.lineWidth = 1.5
    ctx.setLineDash([6, 4])
    ctx.beginPath()
    ctx.moveTo(pts[0][0], pts[0][1])
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1])
    ctx.stroke()
    ctx.setLineDash([])
  }

  /* 闭合多边形 */
  if (pts.length >= 3) {
    ctx.strokeStyle = '#d94a4a'
    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.moveTo(pts[0][0], pts[0][1])
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1])
    ctx.closePath()
    ctx.stroke()
    ctx.fillStyle = 'rgba(217, 74, 74, 0.08)'
    ctx.fill()
  }

  /* 顶点 */
  pts.forEach((p, i) => {
    /* 外环 */
    ctx.fillStyle = pts.length >= 3 ? '#d94a4a' : '#d4993c'
    ctx.beginPath()
    ctx.arc(p[0], p[1], 5, 0, Math.PI * 2)
    ctx.fill()
    /* 内芯 */
    ctx.fillStyle = '#fff'
    ctx.beginPath()
    ctx.arc(p[0], p[1], 2.5, 0, Math.PI * 2)
    ctx.fill()
  })
}

function onCanvasClick(ev: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = (ev.clientX - rect.left) / rect.width
  const y = (ev.clientY - rect.top) / rect.height
  const newPoints: RoiPoint[] = [
    ...props.points,
    [Math.max(0, Math.min(1, x)), Math.max(0, Math.min(1, y))],
  ]
  emit('update:points', newPoints)
}

watch(() => props.points, () => draw(), { deep: true })

onMounted(async () => {
  await nextTick()
  draw()
})
</script>

<style scoped>
.canvas-wrap {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  overflow: hidden;
  background: #080b10;
}

.roi {
  width: 100%;
  height: auto;
  display: block;
  cursor: crosshair;
}
</style>
