<template>
  <div class="page">
    <PageHeader title="实时监控">
      <template #extra>
        <div class="controls">
          <span class="ws-badge" :class="store.running ? 'live' : 'idle'">
            <span class="ws-dot" />
            {{ store.running ? '监控中' : '已停止' }}
          </span>
          <el-button
            v-if="!store.running"
            type="primary"
            @click="store.start()"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none" style="margin-right:6px;vertical-align:-2px"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            开启监控
          </el-button>
          <el-button
            v-if="store.running"
            @click="store.stop()"
          >
            停止
          </el-button>
        </div>
      </template>
    </PageHeader>

    <div class="main">
      <!-- 视频区域 -->
      <div class="video-section">
        <VideoStream :jpeg-src="store.jpegSrc" @load="store.onStreamFrameDecoded">
          <StatsOverlay
            :visible="store.running"
            :fps="store.statsFps"
            :latency="store.latencyLabel"
          />
        </VideoStream>
      </div>

      <!-- 右侧面板 -->
      <div class="side-panel">
        <AlarmPanel :alarms="store.alarms" />

        <!-- 业务规则 -->
        <details class="rules-panel" open>
          <summary class="rules-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            告警规则说明
          </summary>
          <ul class="rules-list">
            <li>
              <span class="rule-badge fire">火灾</span>
              <span>同一区域连续多帧高置信度确认</span>
            </li>
            <li>
              <span class="rule-badge smoke">烟雾</span>
              <span>同一区域连续多帧高置信度确认</span>
            </li>
            <li>
              <span class="rule-badge weapon">刀具/撬棍</span>
              <span>目标中心点位移超过阈值才告警</span>
            </li>
            <li>
              <span class="rule-badge intrusion">门窗/禁区</span>
              <span>人员在敏感区停留后离开或消失</span>
            </li>
          </ul>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import PageHeader from '../components/common/PageHeader.vue'
import VideoStream from '../components/monitor/VideoStream.vue'
import StatsOverlay from '../components/monitor/StatsOverlay.vue'
import AlarmPanel from '../components/monitor/AlarmPanel.vue'
import { useMonitorStore } from '../stores/monitor'

const store = useMonitorStore()

onBeforeUnmount(() => store.stop())
</script>

<style scoped>
.page {
  display: grid;
  gap: 16px;
  animation: fade-in-up 0.4s var(--ease-out);
}

.controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ws-badge {
  display: flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.05em;
  padding: 5px 12px;
  border-radius: 999px;
  user-select: none;
}

.ws-badge.live {
  color: var(--ok);
  background: var(--ok-glow);
  border: 1px solid rgba(59, 158, 90, 0.2);
}

.ws-badge.idle {
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
}

.ws-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.ws-badge.live .ws-dot {
  animation: amber-breathe 2s ease-in-out infinite;
}

/* ---- 主布局 ---- */
.main {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
  min-height: calc(100vh - 140px);
}

.video-section {
  min-width: 0;
}

.side-panel {
  display: grid;
  gap: 12px;
  align-content: start;
}

/* ---- 规则面板 ---- */
.rules-panel {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  box-shadow: var(--shadow-panel);
  cursor: default;
}

.rules-panel[open] .rules-title {
  margin-bottom: 12px;
}

.rules-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--text-primary);
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
}

.rules-title::-webkit-details-marker {
  display: none;
}

.rules-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.rules-list li {
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: baseline;
  gap: 8px;
  line-height: 1.6;
}

.rule-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.04em;
  padding: 2px 8px;
  border-radius: 999px;
  flex-shrink: 0;
  font-weight: 500;
}

.rule-badge.fire {
  color: #e86161;
  background: rgba(217, 74, 74, 0.1);
}

.rule-badge.smoke {
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
}

.rule-badge.weapon {
  color: var(--accent-light);
  background: var(--accent-glow);
}

.rule-badge.intrusion {
  color: #e86161;
  background: rgba(217, 74, 74, 0.06);
}
</style>
