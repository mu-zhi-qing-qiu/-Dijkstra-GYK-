<script setup>
import { computed } from "vue";

const props = defineProps({
  status: { type: String, default: "connecting" },
  start: { type: Object, required: true },
  end: { type: Object, required: true },
});

const statusMeta = computed(() => {
  switch (props.status) {
    case "online":
      return { text: "服务在线", cls: "online" };
    case "offline":
      return { text: "后端离线", cls: "offline" };
    default:
      return { text: "连接中", cls: "connecting" };
  }
});

const now = new Date().toLocaleDateString("zh-CN", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});
</script>

<template>
  <header class="topnav glass">
    <div class="brand">
      <div class="logo">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
          <path
            d="M12 2.5c3.6 0 6.5 2.9 6.5 6.5 0 4.4-6.5 12-6.5 12S5.5 13.4 5.5 9C5.5 5.4 8.4 2.5 12 2.5Z"
            stroke="url(#g)" stroke-width="1.6" />
          <circle cx="12" cy="9" r="2.4" fill="url(#g)" />
          <defs>
            <linearGradient id="g" x1="4" y1="2" x2="20" y2="22">
              <stop stop-color="#22d3ee" />
              <stop offset="1" stop-color="#8b5cf6" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      <div class="brand-text">
        <h1>校园<span class="grad-text">智航</span></h1>
        <p>Dynamic Campus Navigation</p>
      </div>
    </div>

    <div class="scenario">
      <div class="endpoint">
        <span class="pin start"></span>
        <div class="ep-text">
          <small>起点</small>
          <strong>{{ start.name }}</strong>
        </div>
        <span class="code">{{ start.code }}</span>
      </div>
      <div class="arrow">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
          <path d="M4 12h15m0 0-5-5m5 5-5 5" stroke="currentColor" stroke-width="1.7"
            stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <div class="endpoint">
        <span class="pin end"></span>
        <div class="ep-text">
          <small>终点</small>
          <strong>{{ end.name }}</strong>
        </div>
        <span class="code">{{ end.code }}</span>
      </div>
    </div>

    <div class="meta">
      <span class="date">{{ now }}</span>
      <div class="status" :class="statusMeta.cls">
        <span class="led"></span>
        {{ statusMeta.text }}
      </div>
    </div>
  </header>
</template>

<style scoped>
.topnav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-h);
  padding: 0 20px;
  gap: 16px;
}

/* 品牌 */
.brand {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 0;
}
.logo {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 13px;
  background: linear-gradient(145deg, rgba(34, 211, 238, 0.16), rgba(139, 92, 246, 0.16));
  border: 1px solid var(--stroke-strong);
  box-shadow: var(--glow-cyan);
}
.brand-text h1 {
  font-size: 19px;
  font-weight: 800;
  letter-spacing: 0.04em;
  line-height: 1.1;
}
.brand-text p {
  font-size: 10.5px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--text-2);
}

/* 场景 */
.scenario {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 7px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--stroke);
}
.endpoint {
  display: flex;
  align-items: center;
  gap: 9px;
}
.pin {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}
.pin.start {
  background: var(--green);
  box-shadow: 0 0 12px var(--green);
}
.pin.end {
  background: var(--rose);
  box-shadow: 0 0 12px var(--rose);
}
.ep-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}
.ep-text small {
  font-size: 9.5px;
  letter-spacing: 0.16em;
  color: var(--text-2);
}
.ep-text strong {
  font-size: 13.5px;
  font-weight: 700;
}
.code {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 6px;
  color: var(--text-1);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--stroke);
}
.arrow {
  color: var(--cyan);
  display: grid;
  place-items: center;
}

/* 元信息 */
.meta {
  display: flex;
  align-items: center;
  gap: 14px;
}
.date {
  font-size: 12px;
  color: var(--text-2);
  font-variant-numeric: tabular-nums;
}
.status {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 99px;
  border: 1px solid var(--stroke);
}
.status .led {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.status.online {
  color: var(--green);
  background: rgba(52, 211, 153, 0.1);
}
.status.online .led {
  background: var(--green);
  box-shadow: 0 0 10px var(--green);
  animation: pulse-dot 1.8s ease-in-out infinite;
}
.status.offline {
  color: var(--rose);
  background: rgba(251, 113, 133, 0.1);
}
.status.offline .led {
  background: var(--rose);
  box-shadow: 0 0 10px var(--rose);
}
.status.connecting {
  color: var(--amber);
  background: rgba(251, 191, 36, 0.1);
}
.status.connecting .led {
  background: var(--amber);
  animation: pulse-dot 1s ease-in-out infinite;
}

@media (max-width: 1180px) {
  .scenario {
    display: none;
  }
}
@media (max-width: 760px) {
  .brand-text p {
    display: none;
  }
  .date {
    display: none;
  }
}
</style>
