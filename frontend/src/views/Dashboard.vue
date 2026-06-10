<template>
  <div class="page">
    <PageHeader title="首页概览">
      <template #extra>
        <span class="datestamp" :title="dateLabel">{{ dateLabel }}</span>
      </template>
    </PageHeader>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <!-- 今日告警 — 根据是否安全着色 -->
      <div class="stat-card" :class="store.todayCount === 0 ? 'safe' : 'warn'">
        <div class="stat-icon">
          <svg v-if="store.todayCount === 0" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ store.todayCount }}</span>
          <span class="stat-label">今日告警</span>
        </div>
        <div class="stat-status">{{ store.todayCount === 0 ? '一切正常' : '有待处理' }}</div>
      </div>

      <!-- 累计告警 -->
      <div class="stat-card neutral">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ store.totalCount }}</span>
          <span class="stat-label">累计告警</span>
        </div>
      </div>

      <!-- 检测目标 -->
      <div class="stat-card span2 neutral">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </div>
        <div class="stat-body-row">
          <span class="stat-label">检测目标类型</span>
          <div class="targets">
            <span v-for="t in targets" :key="t.name" class="target-chip" :class="t.level">
              {{ t.icon }} {{ t.name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 告警类型分布 -->
    <div class="panel alarms-section">
      <h3 class="section-title">告警类型分布</h3>
      <div v-if="store.events.length === 0" class="empty">
        <div class="empty-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <p class="muted">暂无告警记录，系统运行正常</p>
      </div>
      <div v-else class="alarm-type-grid">
        <div v-for="a in alarmSummary" :key="a.type" class="alarm-type-item">
          <div class="alarm-type-bar">
            <div class="bar-fill" :class="a.level" :style="{ width: a.percent + '%' }" />
          </div>
          <div class="alarm-type-info">
            <span class="alarm-type-name">{{ a.label }}</span>
            <span class="alarm-type-count">{{ a.count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../components/common/PageHeader.vue'
import { useEventsStore } from '../stores/events'
import { alarmTypeZh } from '../utils/alarm'

const store = useEventsStore()

const targets = [
  { name: '人员', icon: '👤', level: 'neutral' },
  { name: '猫', icon: '🐱', level: 'neutral' },
  { name: '狗', icon: '🐕', level: 'neutral' },
  { name: '刀具', icon: '🔪', level: 'danger' },
  { name: '火灾', icon: '🔥', level: 'danger' },
  { name: '烟雾', icon: '💨', level: 'warn' },
  { name: '门窗', icon: '🚪', level: 'warn' },
  { name: '撬棍', icon: '🔧', level: 'danger' },
]

const alarmSummary = computed(() => {
  const counts: Record<string, number> = {}
  store.events.forEach((e) => {
    const zh = alarmTypeZh(e.alarm_type)
    counts[zh] = (counts[zh] || 0) + 1
  })
  const max = Math.max(1, ...Object.values(counts))
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([type, count]) => {
      const levelMap: Record<string, string> = {
        '火灾': 'danger', '烟雾': 'warn', '闯入': 'danger', '危险移动': 'warn',
      }
      return {
        type,
        label: type,
        count,
        percent: Math.round((count / max) * 100),
        level: levelMap[type] || 'neutral',
      }
    })
})

const now = ref(new Date())
const dateLabel = computed(() => {
  const d = now.value
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
  return `${y}年${m}月${day}日 ${week}`
})

onMounted(() => store.fetchEvents())
</script>

<style scoped>
.page {
  display: grid;
  gap: 20px;
  animation: fade-in-up 0.4s var(--ease-out);
}

.datestamp {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

/* ---- 统计卡片 ---- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.span2 {
  grid-column: span 2;
}

.stat-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-panel);
  transition: all var(--duration-normal) var(--ease-out);
  cursor: default;
  position: relative;
  overflow: hidden;
}

.stat-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-out);
  pointer-events: none;
}

.stat-card.safe::after {
  background: radial-gradient(ellipse at left center, var(--ok-glow), transparent 70%);
  opacity: 1;
}

.stat-card.warn::after {
  background: radial-gradient(ellipse at left center, var(--warn-glow), transparent 70%);
  opacity: 1;
}

.stat-card:hover {
  border-color: var(--border-default);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.stat-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.stat-card.safe .stat-icon {
  color: var(--ok);
  background: var(--ok-glow);
}

.stat-card.warn .stat-icon {
  color: var(--accent);
  background: var(--accent-glow);
}

.stat-card.neutral .stat-icon {
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.04);
}

.stat-body {
  display: grid;
  gap: 2px;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 36px;
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-status {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.05em;
  padding: 5px 12px;
  border-radius: 999px;
  position: relative;
  z-index: 1;
  font-weight: 500;
}

.stat-card.safe .stat-status {
  color: var(--ok);
  background: var(--ok-glow);
}

.stat-card.warn .stat-status {
  color: var(--accent);
  background: var(--accent-glow);
}

/* 检测目标 */
.stat-body-row {
  display: grid;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.targets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.target-chip {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid var(--border-default);
  background: var(--bg-root);
  color: var(--text-secondary);
  transition: all var(--duration-fast) var(--ease-out);
}

.target-chip.danger {
  border-color: rgba(217, 74, 74, 0.25);
  background: rgba(217, 74, 74, 0.06);
  color: #e86161;
}

.target-chip.warn {
  border-color: rgba(212, 153, 60, 0.25);
  background: rgba(212, 153, 60, 0.06);
  color: var(--accent-light);
}

.target-chip:hover {
  border-color: var(--border-emphasis);
  color: var(--text-primary);
}

/* ---- 告警分布 ---- */
.alarms-section {
  padding: 18px 20px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 400;
  margin: 0 0 16px;
  letter-spacing: 0.02em;
  color: var(--text-primary);
}

.empty {
  text-align: center;
  padding: 32px 0;
}

.empty-icon {
  color: var(--ok);
  margin-bottom: 10px;
  opacity: 0.6;
}

.alarm-type-grid {
  display: grid;
  gap: 12px;
}

.alarm-type-item {
  display: grid;
  gap: 6px;
}

.alarm-type-bar {
  height: 6px;
  border-radius: 3px;
  background: var(--bg-root);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.6s var(--ease-out);
}

.bar-fill.danger {
  background: var(--danger);
  box-shadow: 0 0 6px var(--danger-glow);
}

.bar-fill.warn {
  background: var(--accent);
  box-shadow: 0 0 6px var(--accent-glow);
}

.bar-fill.neutral {
  background: var(--text-muted);
}

.alarm-type-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alarm-type-name {
  font-size: 13px;
  color: var(--text-secondary);
}

.alarm-type-count {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}
</style>
