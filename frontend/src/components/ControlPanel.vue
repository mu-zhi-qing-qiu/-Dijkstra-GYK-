<script setup>
import PlacePicker from "./PlacePicker.vue";
import { MODES, PERIODS } from "../utils.js";

const props = defineProps({
  mode: { type: String, required: true },
  period: { type: String, required: true },
  startId: { type: Number, default: null },
  endId: { type: Number, default: null },
  places: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits([
  "update:mode",
  "update:period",
  "update:startId",
  "update:endId",
]);

function swap() {
  const s = props.startId;
  emit("update:startId", props.endId);
  emit("update:endId", s);
}
</script>

<template>
  <div class="panel glass anim-rise">
    <div class="panel-title"><span class="dot"></span>行程规划</div>

    <!-- 起终点选择 -->
    <div class="route-box">
      <PlacePicker
        :model-value="startId"
        :places="places"
        accent="start"
        placeholder="选择起点"
        @update:model-value="emit('update:startId', $event)"
      />
      <div class="rail">
        <span class="rail-line"></span>
        <button class="swap" title="对调起终点" @click="swap">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none">
            <path d="M7 4v13m0 0-3-3m3 3 3-3M17 20V7m0 0 3 3m-3-3-3 3"
              stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
      </div>
      <PlacePicker
        :model-value="endId"
        :places="places"
        accent="end"
        placeholder="选择终点"
        @update:model-value="emit('update:endId', $event)"
      />
    </div>

    <!-- 出行方式 -->
    <div class="group">
      <label class="group-label">出行方式</label>
      <div class="mode-grid">
        <button
          v-for="m in MODES"
          :key="m.value"
          class="mode-card"
          :class="{ active: mode === m.value }"
          :style="{ '--accent': m.grad }"
          @click="emit('update:mode', m.value)"
        >
          <span class="mc-icon">
            <svg v-if="m.value === 'walk'" viewBox="0 0 24 24" width="22" height="22" fill="none">
              <circle cx="13" cy="4" r="1.8" fill="currentColor" />
              <path d="M11 21l2-5-2.5-2.2.8-4.3L9 11l-2 2m6.5-2 2.2 1.4L17 16M11.5 9.5 14 8l2.2 1.5"
                stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="none">
              <circle cx="5.5" cy="17" r="3.2" stroke="currentColor" stroke-width="1.6" />
              <circle cx="18.5" cy="17" r="3.2" stroke="currentColor" stroke-width="1.6" />
              <path d="M8 17h4l3-6 2 6M9 8h3l3 3m-3-3 .5-2"
                stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
              <circle cx="15" cy="5.4" r="1.4" fill="currentColor" />
            </svg>
          </span>
          <span class="mc-text">
            <strong>{{ m.label }}</strong>
            <small>{{ m.desc }}</small>
          </span>
          <span class="mc-check" v-if="mode === m.value">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none">
              <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2.2"
                stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
        </button>
      </div>
    </div>

    <!-- 时段（全部 4 个） -->
    <div class="group">
      <label class="group-label">时段模式</label>
      <div class="period-grid">
        <button
          v-for="p in PERIODS"
          :key="p.value"
          class="period-chip"
          :class="{ active: period === p.value }"
          @click="emit('update:period', p.value)"
        >
          <span class="pc-level" :class="p.level"></span>
          <span class="pc-text">
            <strong>{{ p.label }}</strong>
            <small>{{ p.desc }}</small>
          </span>
        </button>
      </div>
    </div>

    <div class="hint">
      <span class="spinner" v-if="loading"></span>
      <span v-if="loading">正在重新规划路线…</span>
      <span v-else>调整起终点 / 方式 / 时段即实时规划</span>
    </div>
  </div>
</template>

<style scoped>
.panel {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 起终点 */
.route-box {
  position: relative;
  padding: 14px;
  border-radius: var(--r-md);
  background: rgba(255, 255, 255, 0.03);

}
.rail {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 14px;
  margin: 7px 0;
}
.rail-line {
  position: absolute;
  left: 19px;
  top: 50%;
  width: 1px;
  height: 22px;
  transform: translateY(-50%);
  background: repeating-linear-gradient(to bottom, var(--text-2) 0 3px, transparent 3px 7px);
}
.swap {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  color: var(--cyan);
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.25);
  cursor: pointer;
  transition: transform 0.25s, background 0.2s;
}
.swap:hover {
  background: rgba(34, 211, 238, 0.2);
  transform: rotate(180deg);
}

/* 分组 */
.group {
  display: flex;
  flex-direction: column;
  gap: 9px;
}
.group-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: var(--text-2);
  text-transform: uppercase;
}

/* 出行方式卡片 */
.mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.mode-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 13px;
  border-radius: var(--r-md);
  background: var(--surface-2);
  border: 1px solid var(--stroke);
  color: var(--text-1);
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s, border-color 0.25s, color 0.25s, box-shadow 0.3s;
}
.mode-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--accent);
  opacity: 0;
  transition: opacity 0.3s;
}
.mode-card > * {
  position: relative;
  z-index: 1;
}
.mode-card:hover {
  transform: translateY(-2px);
  border-color: var(--stroke-strong);
}
.mode-card.active {
  color: #07101d;
  border-color: transparent;
  box-shadow: 0 12px 26px -12px rgba(34, 211, 238, 0.6);
}
.mode-card.active::before {
  opacity: 1;
}
.mc-icon {
  display: grid;
  place-items: center;
}
.mc-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.mc-text strong {
  font-size: 14px;
  font-weight: 700;
}
.mc-text small {
  font-size: 10.5px;
  opacity: 0.85;
}
.mc-check {
  position: absolute;
  top: 7px;
  right: 7px;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.22);
}

/* 时段网格 2x2 */
.period-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.period-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: var(--r-sm);
  background: var(--surface-2);
  border: 1px solid var(--stroke);
  color: var(--text-1);
  cursor: pointer;
  text-align: left;
  transition: transform 0.18s, border-color 0.25s, background 0.25s, box-shadow 0.3s;
}
.period-chip:hover {
  transform: translateY(-1px);
  border-color: var(--stroke-strong);
}
.period-chip.active {
  border-color: rgba(34, 211, 238, 0.5);
  background: rgba(34, 211, 238, 0.1);
  box-shadow: 0 10px 22px -14px rgba(34, 211, 238, 0.7), inset 0 0 0 1px rgba(34, 211, 238, 0.2);
}
.pc-level {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}
.pc-level.low {
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
}
.pc-level.mid {
  background: var(--amber);
  box-shadow: 0 0 8px var(--amber);
}
.pc-level.high {
  background: var(--rose);
  box-shadow: 0 0 8px var(--rose);
}
.pc-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  min-width: 0;
}
.pc-text strong {
  font-size: 13.5px;
  font-weight: 700;
}
.period-chip.active .pc-text strong {
  color: var(--cyan);
}
.pc-text small {
  font-size: 10px;
  color: var(--text-2);
}

/* 提示 */
.hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  color: var(--text-2);
  padding-top: 2px;
}
.spinner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(34, 211, 238, 0.25);
  border-top-color: var(--cyan);
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
</style>
