<template>
  <div class="page">
    <PageHeader title="事件记录" />

    <EventsTable
      :events="store.events"
      @delete="remove"
      @batch-delete="batchRemove"
      @row-click="openRow"
    />

    <ImagePreview
      v-model="dialogVisible"
      :image-url="activeRow?.image_url ?? ''"
      :alarm-type="activeRow?.alarm_type ?? ''"
      :time="activeRow?.created_at ?? ''"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import EventsTable from '../components/events/EventsTable.vue'
import ImagePreview from '../components/events/ImagePreview.vue'
import { useEventsStore } from '../stores/events'
import type { SecurityEvent } from '../stores/events'

const store = useEventsStore()
const dialogVisible = ref(false)
const activeRow = ref<SecurityEvent | null>(null)

function openRow(row: SecurityEvent) {
  activeRow.value = row
  dialogVisible.value = true
}

async function remove(row: SecurityEvent) {
  try {
    await ElMessageBox.confirm('确认删除该事件记录及对应图片文件？', '提示', { type: 'warning' })
    await store.deleteEvent(row.id)
    ElMessage.success('已删除')
  } catch (_e) {}
}

async function batchRemove(ids: number[]) {
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${ids.length} 条事件记录及对应图片文件？`, '批量删除提示', { type: 'warning' })
    await store.batchDeleteEvents(ids)
    ElMessage.success(`已删除 ${ids.length} 条`)
  } catch (_e) {}
}

onMounted(() => store.fetchEvents())
</script>

<style scoped>
.page {
  display: grid;
  gap: 16px;
  animation: fade-in-up 0.4s var(--ease-out);
}
</style>
