<template>
  <div class="alarm-panel">
    <div class="alarm-header">
      <span class="alarm-title">最新告警</span>
      <span v-if="alarms.length" class="alarm-count">{{ alarms.length }}</span>
    </div>

    <div v-if="alarms.length === 0" class="alarm-empty">
      <div class="no-alarm-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      </div>
      <span>暂无告警</span>
    </div>

    <TransitionGroup v-else name="alarm-list" tag="div" class="alarm-list">
      <div
        v-for="a in alarms"
        :key="`${a.alarm_type}-${a.message}`"
        class="alarm-card"
        :class="levelClass(a.level)"
      >
        <div class="alarm-top">
          <span class="alarm-type-badge" :class="levelClass(a.level)">
            {{ a.alarm_type }}
          </span>
          <span class="alarm-lv" :class="levelClass(a.level)">{{ a.level }}</span>
        </div>
        <p class="alarm-msg">{{ a.message }}</p>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import type { FrameAlarm } from '../../stores/monitor'

defineProps<{
  alarms: FrameAlarm[]
}>()

function levelClass(level: string): string {
  if (level === 'HIGH') return 'high'
  if (level === 'MEDIUM') return 'medium'
  return 'low'
}
</script>

<style scoped>
.alarm-panel {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  box-shadow: var(--shadow-panel);
}

.alarm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.alarm-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 400;
  letter-spacing: 0.02em;
}

.alarm-count {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--accent-glow);
  color: var(--accent-light);
  font-weight: 600;
}

/* 空状态 */
.alarm-empty {
  text-align: center;
  padding: 20px 0 8px;
  color: var(--text-muted);
  font-size: 13px;
}

.no-alarm-icon {
  color: var(--ok);
  opacity: 0.4;
  margin-bottom: 8px;
}

/* 告警列表 */
.alarm-list {
  display: grid;
  gap: 8px;
  max-height: 360px;
  overflow-y: auto;
}

.alarm-card {
  padding: 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  background: var(--bg-root);
  transition: all var(--duration-fast) var(--ease-out);
}

.alarm-card.high {
  border-color: rgba(217, 74, 74, 0.2);
  background: rgba(217, 74, 74, 0.04);
  animation: alarm-pulse 2s ease-in-out 1;
}

.alarm-card.medium {
  border-color: rgba(212, 153, 60, 0.2);
  background: rgba(212, 153, 60, 0.04);
}

.alarm-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.alarm-type-badge {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.alarm-type-badge.high {
  color: #e86161;
  background: rgba(217, 74, 74, 0.12);
}

.alarm-type-badge.medium {
  color: var(--accent-light);
  background: var(--accent-glow);
}

.alarm-lv {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.06em;
}

.alarm-lv.high { color: #e86161; }
.alarm-lv.medium { color: var(--accent-light); }

.alarm-msg {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 列表动画 */
.alarm-list-enter-active {
  transition: all 0.3s var(--ease-out);
}

.alarm-list-leave-active {
  transition: all 0.2s ease-in;
}

.alarm-list-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.alarm-list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
