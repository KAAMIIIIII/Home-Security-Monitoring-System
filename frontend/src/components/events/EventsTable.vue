<template>
  <div class="table-wrap">
    <!-- 批量操作栏 -->
    <transition name="batch-bar">
      <div v-if="selectedIds.length" class="batch-bar">
        <span class="batch-hint">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          已选择 {{ selectedIds.length }} 条记录
        </span>
        <el-button type="danger" size="small" @click="onBatchRemove">批量删除</el-button>
      </div>
    </transition>

    <el-table
      ref="tableRef"
      :data="events"
      style="width: 100%"
      @row-click="(row: SecurityEvent) => $emit('row-click', row)"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="44" />
      <el-table-column label="告警时间" width="220">
        <template #default="{ row }: { row: SecurityEvent }">
          <span class="time-cell">{{ fmt(row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="告警类型" width="170">
        <template #default="{ row }: { row: SecurityEvent }">
          <span class="alarm-type-cell" :class="levelClass(row.alarm_type)">{{ alarmTypeZh(row.alarm_type) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="抓拍画面" min-width="200">
        <template #default="{ row }: { row: SecurityEvent }">
          <div class="thumb-wrap">
            <img class="thumb" :src="row.image_url" alt="抓拍画面" loading="lazy" />
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }: { row: SecurityEvent }">
          <el-button type="danger" size="small" plain @click.stop="$emit('delete', row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ElTable } from 'element-plus'
import type { SecurityEvent } from '../../stores/events'
import { alarmTypeZh } from '../../utils/alarm'
import { fmt } from '../../utils/date'

defineProps<{
  events: SecurityEvent[]
}>()

const emit = defineEmits<{
  delete: [row: SecurityEvent]
  'batch-delete': [ids: number[]]
  'row-click': [row: SecurityEvent]
}>()

const tableRef = ref<InstanceType<typeof ElTable>>()
const selectedIds = ref<number[]>([])

function onSelectionChange(rows: SecurityEvent[]) {
  selectedIds.value = rows.map((r) => r.id)
}

function onBatchRemove() {
  emit('batch-delete', [...selectedIds.value])
  tableRef.value?.clearSelection()
}

function levelClass(alarmType: string): string {
  if (alarmType === 'Fire' || alarmType === 'Intrusion') return 'high'
  if (alarmType === 'Smoke' || alarmType === 'WeaponMove') return 'medium'
  return 'neutral'
}
</script>

<style scoped>
.table-wrap {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 14px;
  box-shadow: var(--shadow-panel);
}

/* 批量操作栏 */
.batch-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  margin-bottom: 12px;
  background: rgba(217, 74, 74, 0.06);
  border: 1px solid rgba(217, 74, 74, 0.2);
  border-radius: var(--radius-md);
}

.batch-hint {
  color: #e86161;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.batch-bar-enter-active,
.batch-bar-leave-active {
  transition: all 0.25s var(--ease-out);
}

.batch-bar-enter-from,
.batch-bar-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* 时间 */
.time-cell {
  font-family: var(--font-mono);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  color: var(--text-secondary);
}

/* 告警类型标签 */
.alarm-type-cell {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  padding: 3px 10px;
  border-radius: 999px;
  display: inline-block;
}

.alarm-type-cell.high {
  color: #e86161;
  background: rgba(217, 74, 74, 0.1);
}

.alarm-type-cell.medium {
  color: var(--accent-light);
  background: var(--accent-glow);
}

.alarm-type-cell.neutral {
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.04);
}

/* 缩略图 */
.thumb-wrap {
  padding: 2px 0;
}

.thumb {
  width: 140px;
  height: 78px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  transition: transform var(--duration-fast) var(--ease-out), border-color var(--duration-fast) var(--ease-out);
  cursor: pointer;
}

.thumb:hover {
  transform: scale(1.03);
  border-color: var(--accent);
}
</style>
