<template>
  <div class="page">
    <PageHeader title="系统设置" />

    <div class="grid">
      <!-- 检测参数 -->
      <div class="panel-elevated card">
        <h3 class="card-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-4px;margin-right:8px"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          检测参数
        </h3>

        <div class="param-group">
          <div class="param">
            <div class="param-head">
              <span class="param-label">置信度阈值</span>
            </div>
            <el-slider v-model="store.conf" :min="0.1" :max="0.9" :step="0.05" show-input />
          </div>

          <div class="param">
            <div class="param-head">
              <span class="param-label">IoU 阈值</span>
            </div>
            <el-slider v-model="store.iou" :min="0.1" :max="0.9" :step="0.05" show-input />
          </div>

          <div class="param">
            <div class="param-head">
              <span class="param-label">告警保留天数</span>
            </div>
            <el-input-number v-model="store.retentionDays" :min="1" :max="60" />
          </div>
        </div>

        <div class="param-actions">
          <el-button type="primary" @click="saveParams">保存参数</el-button>
          <span v-if="saveHint" class="save-hint mono muted">{{ saveHint }}</span>
        </div>
      </div>

      <!-- 禁区绘制 -->
      <div class="panel-elevated card">
        <h3 class="card-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-4px;margin-right:8px"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
          禁区绘制
        </h3>

        <p class="card-desc">点击画布添加多边形顶点，至少 3 个点形成禁区。清空后需点「保存禁区」才会清除后端数据。</p>

        <RoiCanvas v-model:points="store.roiPolygon" />

        <div class="roi-actions">
          <div class="roi-info">
            <span class="roi-count mono">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:4px"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/><line x1="12" y1="22" x2="12" y2="15.5"/></svg>
              {{ store.roiPolygon.length }} 个顶点
            </span>
          </div>
          <div class="roi-buttons">
            <el-button @click="store.roiPolygon = []">清空</el-button>
            <el-button
              type="primary"
              :disabled="store.roiPolygon.length > 0 && store.roiPolygon.length < 3"
              @click="saveRoi"
            >
              保存禁区
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import RoiCanvas from '../components/settings/RoiCanvas.vue'
import { useSettingsStore } from '../stores/settings'

const store = useSettingsStore()
const saveHint = ref('')

async function saveParams() {
  await store.saveParams()
  saveHint.value = `conf=${store.conf}, iou=${store.iou}, 保留=${store.retentionDays}天`
  ElMessage.success('参数已更新到后端')
}

async function saveRoi() {
  await store.saveRoi()
  if (store.roiPolygon.length === 0) {
    ElMessage.success('禁区已清除')
  } else {
    ElMessage.success('禁区已保存')
  }
}

onMounted(() => store.fetchSettings())
</script>

<style scoped>
.page {
  display: grid;
  gap: 16px;
  animation: fade-in-up 0.4s var(--ease-out);
}

.grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 16px;
  align-items: start;
}

.card {
  padding: 18px 20px;
  display: grid;
  gap: 14px;
}

.card-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 400;
  letter-spacing: 0.02em;
  margin: 0;
  color: var(--text-primary);
}

.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* 参数 */
.param-group {
  display: grid;
  gap: 18px;
}

.param {
  display: grid;
  gap: 6px;
}

.param-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.param-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.param-value {
  font-size: 13px;
  color: var(--accent-light);
  font-weight: 500;
}

.mono {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

.param-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 4px;
}

.save-hint {
  font-size: 12px;
}

/* 禁区 */
.roi-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.roi-info {
  display: flex;
  align-items: center;
}

.roi-count {
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
}

.roi-buttons {
  display: flex;
  gap: 8px;
}
</style>
