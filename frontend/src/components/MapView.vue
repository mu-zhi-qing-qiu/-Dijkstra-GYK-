<script setup>
import { computed, reactive, ref } from "vue";
import { mapLayer, hasDrawnRoute, formatDistance, formatDuration } from "../utils.js";

const props = defineProps({
  mode: { type: String, required: true },
  period: { type: String, required: true },
  loading: { type: Boolean, default: false },
  result: { type: Object, default: null },
  start: { type: Object, required: true },
  end: { type: Object, required: true },
});

const stageRef = ref(null);
const src = computed(() => mapLayer(props.start.id, props.end.id, props.mode, props.period));
const routeDrawn = computed(() =>
  hasDrawnRoute(props.start.id, props.end.id, props.period)
);
const modeLabel = computed(() => (props.mode === "walk" ? "步行" : "自行车"));
const periodLabel = computed(() => {
  const map = { normal: "普通时段", morning_peak: "早高峰", lunch_peak: "午高峰", evening_peak: "晚高峰" };
  return map[props.period] || props.period;
});

// ---- 缩放与平移 ----
const view = reactive({ scale: 1, tx: 0, ty: 0 });
const drag = reactive({ active: false, sx: 0, sy: 0, ox: 0, oy: 0 });

function clampPan() {
  const el = stageRef.value;
  if (!el) return;
  const limX = (el.clientWidth * (view.scale - 1)) / 2;
  const limY = (el.clientHeight * (view.scale - 1)) / 2;
  view.tx = Math.max(-limX, Math.min(limX, view.tx));
  view.ty = Math.max(-limY, Math.min(limY, view.ty));
}
function setScale(next) {
  view.scale = Math.max(1, Math.min(3, +next.toFixed(2)));
  if (view.scale === 1) {
    view.tx = 0;
    view.ty = 0;
  } else clampPan();
}
const zoomIn = () => setScale(view.scale + 0.3);
const zoomOut = () => setScale(view.scale - 0.3);
const reset = () => {
  view.scale = 1;
  view.tx = 0;
  view.ty = 0;
};
function onWheel(e) {
  e.preventDefault();
  setScale(view.scale + (e.deltaY < 0 ? 0.22 : -0.22));
}
function onDown(e) {
  if (view.scale <= 1) return;
  const pt = e.touches ? e.touches[0] : e;
  drag.active = true;
  drag.sx = pt.clientX;
  drag.sy = pt.clientY;
  drag.ox = view.tx;
  drag.oy = view.ty;
}
function onMove(e) {
  if (!drag.active) return;
  if (e.cancelable) e.preventDefault(); // 仅在拖拽时阻止默认，避免影响移动端页面滚动
  const pt = e.touches ? e.touches[0] : e;
  view.tx = drag.ox + (pt.clientX - drag.sx);
  view.ty = drag.oy + (pt.clientY - drag.sy);
  clampPan();
}
const onUp = () => (drag.active = false);
</script>

<template>
  <div class="map glass anim-rise">
    <!-- 顶部信息条 -->
    <div class="map-head">
      <div class="panel-title"><span class="dot"></span>校园地图 · 路线可视化</div>
      <div class="route-chip" :class="mode">
        <span class="line-sample" v-if="routeDrawn"></span>
        <span>{{ modeLabel }} · {{ periodLabel }}</span>
        <span class="chip-tag" v-if="!routeDrawn">示意地图</span>
      </div>
    </div>

    <!-- 地图舞台 -->
    <div
      class="stage"
      ref="stageRef"
      @wheel="onWheel"
      @mousedown="onDown"
      @mousemove="onMove"
      @mouseup="onUp"
      @mouseleave="onUp"
      @touchstart.passive="onDown"
      @touchmove="onMove"
      @touchend="onUp"
      :class="{ grabbing: drag.active, zoomed: view.scale > 1 }"
    >
      <Transition name="imgfade">
        <img
          :key="src"
          :src="src"
          class="map-img"
          alt="校园导航路线图"
          draggable="false"
          :style="{ transform: `translate(${view.tx}px, ${view.ty}px) scale(${view.scale})` }"
        />
      </Transition>

      <!-- HUD 角框 -->
      <span class="bracket tl"></span>
      <span class="bracket tr"></span>
      <span class="bracket bl"></span>
      <span class="bracket br"></span>

      <!-- 加载扫描 -->
      <div class="scan" v-if="loading">
        <span class="scan-line"></span>
        <div class="scan-tip"><span class="spinner"></span>路径规划中…</div>
      </div>

      <!-- 罗盘 -->
      <div class="compass">
        <svg viewBox="0 0 48 48" width="48" height="48">
          <circle cx="24" cy="24" r="21" fill="rgba(8,12,24,0.55)" stroke="rgba(255,255,255,0.18)" />
          <path d="M24 7 L28 24 L24 22 L20 24 Z" fill="#fb7185" />
          <path d="M24 41 L20 24 L24 26 L28 24 Z" fill="rgba(255,255,255,0.45)" />
          <text x="24" y="6.5" fill="#eaf1ff" font-size="6" text-anchor="middle" font-weight="700">N</text>
        </svg>
      </div>

      <!-- 缩放控制 -->
      <div class="zoom">
        <button @click="zoomIn" title="放大">+</button>
        <span class="zoom-val">{{ Math.round(view.scale * 100) }}%</span>
        <button @click="zoomOut" title="缩小">−</button>
        <button class="reset" @click="reset" title="复位">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none">
            <path d="M4 9a8 8 0 1 1-.5 5M4 9V4m0 5h5" stroke="currentColor"
              stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
      </div>

      <!-- 概览 HUD -->
      <div class="overview" v-if="result">
        <div class="ov-item">
          <small>距离</small>
          <strong>{{ formatDistance(result.distance) }}</strong>
        </div>
        <span class="ov-sep"></span>
        <div class="ov-item">
          <small>耗时</small>
          <strong>{{ formatDuration(result.time) }}</strong>
        </div>
        <span class="ov-sep"></span>
        <div class="ov-item">
          <small>节点</small>
          <strong>{{ result.path?.length || 0 }}</strong>
        </div>
      </div>
    </div>

    <!-- 底部图例 -->
    <div class="legend">
      <div class="lg-item"><span class="lg-dot start"></span>起点 {{ start.name }}</div>
      <div class="lg-item" v-if="routeDrawn"><span class="lg-line"></span>推荐路线</div>
      <div class="lg-item" v-else><span class="lg-line plain"></span>普通地图 · 暂无预绘制路线</div>
      <div class="lg-item"><span class="lg-dot end"></span>终点 {{ end.name }}</div>
      <div class="lg-note">提示图层 · 滚轮缩放 / 拖拽平移</div>
    </div>
  </div>
</template>

<style scoped>
.map {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 14px;
  gap: 12px;
  overflow: hidden;
}
.map-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.route-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--stroke);
  color: var(--text-1);
}
.line-sample {
  width: 18px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, #ff4d6d, #ff8a5b);
  box-shadow: 0 0 8px rgba(255, 77, 109, 0.7);
}
.chip-tag {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 99px;
  color: var(--amber);
  background: rgba(251, 191, 36, 0.12);
  border: 1px solid rgba(251, 191, 36, 0.3);
}

/* 舞台 */
.stage {
  position: relative;
  flex: 1;
  min-height: 0;
  border-radius: var(--r-md);
  overflow: hidden;
  background: #0a1020;
  border: 1px solid var(--stroke);
  cursor: default;
}
.stage.zoomed {
  cursor: grab;
}
.stage.grabbing {
  cursor: grabbing;
}
.map-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  user-select: none;
  -webkit-user-drag: none;
  transition: transform 0.15s ease-out;
  will-change: transform;
}
.imgfade-enter-active,
.imgfade-leave-active {
  transition: opacity 0.45s ease;
}
.imgfade-enter-from,
.imgfade-leave-to {
  opacity: 0;
}

/* HUD 角框 */
.bracket {
  position: absolute;
  width: 26px;
  height: 26px;
  border: 2px solid rgba(34, 211, 238, 0.5);
  pointer-events: none;
}
.bracket.tl {
  top: 12px;
  left: 12px;
  border-right: 0;
  border-bottom: 0;
  border-top-left-radius: 8px;
}
.bracket.tr {
  top: 12px;
  right: 12px;
  border-left: 0;
  border-bottom: 0;
  border-top-right-radius: 8px;
}
.bracket.bl {
  bottom: 12px;
  left: 12px;
  border-right: 0;
  border-top: 0;
  border-bottom-left-radius: 8px;
}
.bracket.br {
  bottom: 12px;
  right: 12px;
  border-left: 0;
  border-top: 0;
  border-bottom-right-radius: 8px;
}

/* 扫描 */
.scan {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 90px;
  background: linear-gradient(180deg, transparent, rgba(34, 211, 238, 0.22), transparent);
  border-top: 1px solid rgba(34, 211, 238, 0.7);
  animation: scan 1.7s ease-in-out infinite;
}
.scan-tip {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--cyan);
  padding: 6px 13px;
  border-radius: 99px;
  background: rgba(8, 12, 24, 0.7);
  border: 1px solid rgba(34, 211, 238, 0.35);
}
.spinner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(34, 211, 238, 0.25);
  border-top-color: var(--cyan);
  animation: spin 0.7s linear infinite;
}

/* 罗盘 */
.compass {
  position: absolute;
  top: 14px;
  right: 14px;
  opacity: 0.9;
  pointer-events: none;
}

/* 缩放控制 */
.zoom {
  position: absolute;
  right: 14px;
  bottom: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 6px;
  border-radius: 12px;
  background: rgba(8, 12, 24, 0.6);
  border: 1px solid var(--stroke);
  backdrop-filter: blur(8px);
}
.zoom button {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  border: 1px solid var(--stroke);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-0);
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.zoom button:hover {
  background: rgba(34, 211, 238, 0.16);
  border-color: rgba(34, 211, 238, 0.4);
}
.zoom .reset {
  font-size: 12px;
}
.zoom-val {
  font-size: 10px;
  color: var(--text-2);
  font-variant-numeric: tabular-nums;
}

/* 概览 HUD */
.overview {
  position: absolute;
  left: 14px;
  bottom: 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  border-radius: 13px;
  background: rgba(8, 12, 24, 0.66);
  border: 1px solid var(--stroke);
  backdrop-filter: blur(10px);
  animation: pop 0.4s ease both;
}
.ov-item {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}
.ov-item small {
  font-size: 9.5px;
  letter-spacing: 0.14em;
  color: var(--text-2);
}
.ov-item strong {
  font-size: 15px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.ov-sep {
  width: 1px;
  height: 24px;
  background: var(--stroke-strong);
}

/* 图例 */
.legend {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 11.5px;
  color: var(--text-1);
  padding: 0 4px;
}
.lg-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.lg-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}
.lg-dot.start {
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
}
.lg-dot.end {
  background: var(--rose);
  box-shadow: 0 0 8px var(--rose);
}
.lg-line {
  width: 18px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, #ff4d6d, #ff8a5b);
}
.lg-line.plain {
  background: var(--text-2);
  opacity: 0.6;
}
.lg-note {
  margin-left: auto;
  color: var(--text-2);
}

@media (max-width: 760px) {
  .overview {
    gap: 10px;
    padding: 8px 12px;
  }
  .lg-note {
    display: none;
  }
}
</style>
