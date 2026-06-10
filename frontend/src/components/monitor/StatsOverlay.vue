<template>
  <div v-if="visible" class="stats-overlay" aria-hidden="true">
    <div class="stat-row">
      <span class="stat-k">FPS</span>
      <span class="stat-v mono">{{ fps }}</span>
    </div>
    <div class="stat-row">
      <span class="stat-k">延迟</span>
      <span class="stat-v mono">{{ latency }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  fps: number
  latency: string
}>()
</script>

<style scoped>
.stats-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 4;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-primary);
  pointer-events: none;
  display: grid;
  gap: 2px;
}

.stat-row {
  display: flex;
  gap: 10px;
  align-items: baseline;
  justify-content: space-between;
}

.stat-k {
  color: var(--text-muted);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.stat-v {
  font-weight: 500;
  color: var(--accent-light);
  font-variant-numeric: tabular-nums;
}

.mono {
  font-family: var(--font-mono);
}
</style>
