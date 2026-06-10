<template>
  <el-dialog v-model="visible" width="900px" :close-on-click-modal="false">
    <template #header>
      <div class="dlg-header">
        <span class="dlg-title">告警抓拍详情</span>
        <span v-if="alarmType" class="dlg-type" :class="levelClass(alarmType)">{{ alarmTypeZh(alarmType) }}</span>
      </div>
    </template>

    <div class="dlg">
      <div v-if="imageUrl" class="img-frame">
        <img :src="imageUrl" class="big" alt="告警抓拍" />
      </div>
      <div v-if="alarmType || time" class="meta">
        <div v-if="alarmType" class="meta-row">
          <span class="meta-k">告警类型</span>
          <span class="meta-v">{{ alarmTypeZh(alarmType) }}</span>
        </div>
        <div v-if="time" class="meta-row">
          <span class="meta-k">抓拍时间</span>
          <span class="meta-v mono">{{ fmt(time) }}</span>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { alarmTypeZh } from '../../utils/alarm'
import { fmt } from '../../utils/date'

const props = defineProps<{
  modelValue: boolean
  imageUrl: string
  alarmType: string
  time: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

function levelClass(alarmType: string): string {
  if (alarmType === 'Fire' || alarmType === 'Intrusion') return 'high'
  if (alarmType === 'Smoke' || alarmType === 'WeaponMove') return 'medium'
  return 'neutral'
}
</script>

<style scoped>
.dlg-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dlg-title {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 400;
  letter-spacing: 0.02em;
}

.dlg-type {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  padding: 3px 10px;
  border-radius: 999px;
}

.dlg-type.high {
  color: #e86161;
  background: rgba(217, 74, 74, 0.1);
}

.dlg-type.medium {
  color: var(--accent-light);
  background: var(--accent-glow);
}

.dlg {
  display: grid;
  gap: 14px;
}

.img-frame {
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  background: #000;
}

.big {
  width: 100%;
  display: block;
}

.meta {
  display: grid;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-root);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.meta-k {
  font-size: 13px;
  color: var(--text-secondary);
}

.meta-v {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.mono {
  font-family: var(--font-mono);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}
</style>
