<script setup>
import { computed } from "vue";
import { formatDistance, formatDuration, approxMinutes, buildTextGuide } from "../utils.js";

const props = defineProps({
  result: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: "" },
  mode: { type: String, required: true },
});

defineEmits(["retry"]);

const nodes = computed(() => props.result?.path_names ?? []);
const guide = computed(() => buildTextGuide(props.result, props.mode));
</script>

<template>
  <div class="panel glass anim-rise">
    <div class="panel-title"><span class="dot"></span>导航结果</div>

    <!-- 错误态 -->
    <div v-if="error && !loading" class="state error">
      <div class="state-icon">
        <svg viewBox="0 0 24 24" width="26" height="26" fill="none">
          <path d="M12 8v5m0 3.5h.01M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"
            stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <p class="state-title">无法获取导航结果</p>
      <p class="state-desc">{{ error }}</p>
      <button class="btn btn-primary" @click="$emit('retry')">重新请求</button>
      <p class="state-hint">请确认后端已启动：<code>python main.py</code></p>
    </div>

    <!-- 加载骨架 -->
    <div v-else-if="loading && !result" class="skeleton">
      <div class="sk-row">
        <div class="sk-card"></div>
        <div class="sk-card"></div>
      </div>
      <div class="sk-line" v-for="i in 4" :key="i" :style="{ width: 70 + i * 6 + '%' }"></div>
    </div>

    <!-- 结果 -->
    <template v-else-if="result">
      <div class="stats">
        <div class="stat">
          <div class="stat-ic dist">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
              <path d="M4 14s2-2 8-2 8 2 8 2M9 6l-5 8m11-8 5 8" stroke="currentColor"
                stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
              <circle cx="9" cy="6" r="1.6" fill="currentColor" />
            </svg>
          </div>
          <div class="stat-body">
            <small>总距离</small>
            <strong>{{ formatDistance(result.distance) }}</strong>
          </div>
        </div>
        <div class="stat">
          <div class="stat-ic time">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
              <circle cx="12" cy="13" r="8" stroke="currentColor" stroke-width="1.6" />
              <path d="M12 9v4l3 2M9 2h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
          </div>
          <div class="stat-body">
            <small>预计耗时</small>
            <strong>{{ formatDuration(result.time) }}</strong>
            <em>约 {{ approxMinutes(result.time) }} 分钟</em>
          </div>
        </div>
      </div>

      <!-- 路径节点 -->
      <div class="section">
        <div class="sec-head">
          <span>推荐路线</span>
          <span class="count">{{ nodes.length }} 个节点</span>
        </div>
        <div class="timeline">
          <div
            v-for="(name, i) in nodes"
            :key="i"
            class="tl-node"
            :class="{ start: i === 0, end: i === nodes.length - 1 }"
            :style="{ animationDelay: i * 0.05 + 's' }"
          >
            <div class="tl-marker">
              <span class="tl-dot"></span>
              <span class="tl-rail" v-if="i < nodes.length - 1"></span>
            </div>
            <div class="tl-content">
              <span class="tl-name">{{ name }}</span>
              <span class="tl-tag" v-if="i === 0">起点</span>
              <span class="tl-tag end" v-else-if="i === nodes.length - 1">终点</span>
              <span class="tl-idx" v-else>途经 {{ i }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 文字导航 -->
      <div class="section">
        <div class="sec-head"><span>文字导航说明</span></div>
        <p class="guide">{{ guide }}</p>
      </div>
    </template>

    <!-- 空态 -->
    <div v-else class="state empty">
      <div class="state-icon muted">
        <svg viewBox="0 0 24 24" width="26" height="26" fill="none">
          <path d="M9 20 3 17V4l6 3 6-3 6 3v13l-6-3-6 3Zm0 0V7m6 10V4" stroke="currentColor"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <p class="state-title">尚无导航数据</p>
      <p class="state-desc">选择出行方式与时段即可自动规划路线</p>
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

/* 统计卡 */
.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 11px;
}
.stat {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 14px;
  border-radius: var(--r-md);
  background: var(--surface-2);
  border: 1px solid var(--stroke);
  position: relative;
  overflow: hidden;
}
.stat::after {
  content: "";
  position: absolute;
  top: -40%;
  right: -20%;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  opacity: 0.18;
  filter: blur(18px);
}
.stat-ic {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  flex-shrink: 0;
  color: #07101d;
}
.stat-ic.dist {
  background: var(--grad-walk);
}
.stat-ic.time {
  background: var(--grad-primary);
}
.stat-body {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
  min-width: 0;
}
.stat-body small {
  font-size: 10.5px;
  letter-spacing: 0.12em;
  color: var(--text-2);
}
.stat-body strong {
  font-size: 18px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.stat-body em {
  font-style: normal;
  font-size: 10.5px;
  color: var(--text-2);
}

/* 区块 */
.section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.sec-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-0);
  letter-spacing: 0.04em;
}
.sec-head .count {
  font-size: 10.5px;
  font-weight: 600;
  color: var(--text-2);
  padding: 3px 9px;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--stroke);
}

/* 时间线 */
.timeline {
  display: flex;
  flex-direction: column;
  max-height: 210px;
  overflow-y: auto;
  padding-right: 4px;
}
.tl-node {
  display: flex;
  gap: 12px;
  animation: rise 0.4s ease both;
}
.tl-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 12px;
  flex-shrink: 0;
}
.tl-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  margin-top: 4px;
  background: var(--cyan);
  box-shadow: 0 0 9px rgba(34, 211, 238, 0.6);
  flex-shrink: 0;
}
.tl-node.start .tl-dot {
  background: var(--green);
  box-shadow: 0 0 10px var(--green);
}
.tl-node.end .tl-dot {
  background: var(--rose);
  box-shadow: 0 0 10px var(--rose);
}
.tl-rail {
  width: 2px;
  flex: 1;
  min-height: 16px;
  margin: 2px 0;
  background: linear-gradient(var(--cyan), rgba(34, 211, 238, 0.25));
}
.tl-content {
  display: flex;
  align-items: center;
  gap: 9px;
  padding-bottom: 14px;
  min-width: 0;
}
.tl-name {
  font-size: 13.5px;
  font-weight: 600;
}
.tl-tag {
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  color: var(--green);
  background: rgba(52, 211, 153, 0.12);
}
.tl-tag.end {
  color: var(--rose);
  background: rgba(251, 113, 133, 0.12);
}
.tl-idx {
  font-size: 10px;
  color: var(--text-2);
}

/* 文字导航 */
.guide {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-1);
  padding: 13px 15px;
  border-radius: var(--r-md);
  background: rgba(34, 211, 238, 0.05);
  border: 1px solid rgba(34, 211, 238, 0.14);
  border-left: 3px solid var(--cyan);
}

/* 状态 */
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 9px;
  padding: 26px 16px;
}
.state-icon {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  color: var(--rose);
  background: rgba(251, 113, 133, 0.1);
  border: 1px solid rgba(251, 113, 133, 0.2);
  margin-bottom: 4px;
}
.state-icon.muted {
  color: var(--text-2);
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--stroke);
}
.state-title {
  font-size: 14.5px;
  font-weight: 700;
}
.state-desc {
  font-size: 12px;
  color: var(--text-2);
  max-width: 240px;
}
.state .btn {
  margin-top: 6px;
}
.state-hint {
  font-size: 11px;
  color: var(--text-2);
  margin-top: 2px;
}
.state-hint code {
  color: var(--cyan);
  background: rgba(34, 211, 238, 0.1);
  padding: 1px 6px;
  border-radius: 5px;
  font-size: 11px;
}

/* 骨架 */
.skeleton {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.sk-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 11px;
}
.sk-card {
  height: 66px;
  border-radius: var(--r-md);
}
.sk-line {
  height: 13px;
  border-radius: 7px;
}
.sk-card,
.sk-line {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.04) 25%, rgba(255, 255, 255, 0.09) 37%, rgba(255, 255, 255, 0.04) 63%);
  background-size: 280% 100%;
  animation: shimmer 1.4s ease infinite;
}
</style>
