<template>
  <div class="video-wrap" :class="{ active: !!jpegSrc }">
    <!-- 扫描线效果 -->
    <div v-if="jpegSrc" class="scan-line" />

    <template v-if="jpegSrc">
      <img
        class="video"
        :src="jpegSrc"
        alt="实时监控画面"
        @load="$emit('load')"
      />
      <slot />
      <!-- 四角标记 -->
      <div class="corners">
        <span class="corner tl" /><span class="corner tr" />
        <span class="corner bl" /><span class="corner br" />
      </div>
    </template>

    <div v-else class="empty">
      <div class="empty-icon">
        <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.8" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
          <line x1="8" y1="21" x2="16" y2="21"/>
          <line x1="12" y1="17" x2="12" y2="21"/>
          <line x1="3" y1="7" x2="21" y2="7"/>
        </svg>
      </div>
      <p class="empty-title">等待视频流</p>
      <p class="empty-desc">点击「开启监控」启动摄像头画面与 YOLO 实时检测</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  jpegSrc: string
}>()

defineEmits<{
  load: []
}>()
</script>

<style scoped>
.video-wrap {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: #000;
  min-height: 480px;
  display: grid;
  place-items: center;
  border: 1px solid var(--border-subtle);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3), 0 8px 32px rgba(0, 0, 0, 0.5);
}

.video-wrap.active {
  border-color: var(--border-default);
}

.video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

/* 扫描线 */
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(212, 153, 60, 0.2),
    rgba(212, 153, 60, 0.5),
    rgba(212, 153, 60, 0.2),
    transparent
  );
  z-index: 3;
  pointer-events: none;
  animation: scan-line 3s linear infinite;
}

/* 四角标记 */
.corners {
  position: absolute;
  inset: 12px;
  pointer-events: none;
  z-index: 2;
  opacity: 0.3;
  transition: opacity var(--duration-normal) var(--ease-out);
}

.video-wrap:hover .corners {
  opacity: 0.6;
}

.corner {
  position: absolute;
  width: 18px;
  height: 18px;
  border-color: var(--accent);
  border-style: solid;
}

.corner.tl { top: 0; left: 0; border-width: 1px 0 0 1px; }
.corner.tr { top: 0; right: 0; border-width: 1px 1px 0 0; }
.corner.bl { bottom: 0; left: 0; border-width: 0 0 1px 1px; }
.corner.br { bottom: 0; right: 0; border-width: 0 1px 1px 0; }

/* 空状态 */
.empty {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  color: var(--text-muted);
  opacity: 0.3;
  margin-bottom: 16px;
}

.empty-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 400;
  color: var(--text-secondary);
  margin: 0 0 8px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}
</style>
