<script setup>
import { computed, onMounted, ref, watch } from "vue";
import TopNav from "./components/TopNav.vue";
import ControlPanel from "./components/ControlPanel.vue";
import MapView from "./components/MapView.vue";
import ResultPanel from "./components/ResultPanel.vue";
import AiAssistant from "./components/AiAssistant.vue";
import { fetchHealth, fetchNavigation, fetchPlaces } from "./api.js";
import { EXAMPLE } from "./utils.js";

const places = ref([]);
const startId = ref(EXAMPLE.startId);
const endId = ref(EXAMPLE.endId);
const mode = ref("walk");
const period = ref("normal");

const result = ref(null);
const loading = ref(false);
const error = ref("");
const status = ref("connecting"); // connecting | online | offline

const placeById = computed(() =>
  Object.fromEntries(places.value.map((p) => [p.id, p]))
);
const startPlace = computed(
  () => placeById.value[startId.value] || { id: startId.value, name: "—", code: "" }
);
const endPlace = computed(
  () => placeById.value[endId.value] || { id: endId.value, name: "—", code: "" }
);

let reqToken = 0;

async function runNavigation() {
  if (startId.value == null || endId.value == null) return;
  const token = ++reqToken;
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchNavigation({
      start: startId.value,
      end: endId.value,
      mode: mode.value,
      period: period.value,
    });
    if (token !== reqToken) return; // 丢弃过期响应
    result.value = data;
    status.value = "online";
  } catch (e) {
    if (token !== reqToken) return;
    result.value = null;
    error.value = e.message || "导航请求失败";
    status.value = "offline";
  } finally {
    if (token === reqToken) loading.value = false;
  }
}

onMounted(async () => {
  try {
    await fetchHealth();
    status.value = "online";
  } catch {
    status.value = "offline";
  }
  try {
    places.value = await fetchPlaces();
  } catch {
    /* 地点列表获取失败时仍可使用默认示例场景 */
  }
  runNavigation();
});

watch([startId, endId, mode, period], runNavigation);
</script>

<template>
  <div class="app-shell">
    <div class="aurora aurora-1"></div>
    <div class="aurora aurora-2"></div>

    <TopNav :status="status" :start="startPlace" :end="endPlace" />

    <main class="workspace">
      <section class="col-left">
        <ControlPanel
          v-model:mode="mode"
          v-model:period="period"
          v-model:start-id="startId"
          v-model:end-id="endId"
          :places="places"
          :loading="loading"
        />
        <ResultPanel
          :result="result"
          :loading="loading"
          :error="error"
          :mode="mode"
          @retry="runNavigation"
        />
      </section>

      <section class="col-map">
        <MapView
          :mode="mode"
          :period="period"
          :loading="loading"
          :result="result"
          :start="startPlace"
          :end="endPlace"
        />
      </section>

      <section class="col-ai">
        <AiAssistant
          :result="result"
          :mode="mode"
          :period="period"
          :start="startPlace"
          :end="endPlace"
        />
      </section>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  position: relative;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: var(--gap);
  gap: var(--gap);
}

.workspace {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(330px, 364px) minmax(0, 1fr) minmax(360px, 404px);
  grid-template-areas: "left map ai";
  gap: var(--gap);
}

.col-left {
  grid-area: left;
  display: flex;
  flex-direction: column;
  gap: var(--gap);
  min-height: 0;
  overflow-y: auto;
  padding-right: 2px;
}
.col-map {
  grid-area: map;
  min-height: 0;
}
.col-ai {
  grid-area: ai;
  min-height: 0;
}

/* 动态背景光团 */
.aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  pointer-events: none;
  z-index: 0;
  opacity: 0.5;
}
.aurora-1 {
  width: 520px;
  height: 520px;
  top: -180px;
  left: -120px;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.4), transparent 70%);
  animation: float-blob 18s ease-in-out infinite;
}
.aurora-2 {
  width: 560px;
  height: 560px;
  bottom: -220px;
  right: -140px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.4), transparent 70%);
  animation: float-blob 22s ease-in-out infinite reverse;
}

.app-shell > :not(.aurora) {
  position: relative;
  z-index: 1;
}

/* 平板：地图占满顶部，控制与 AI 并排 */
@media (max-width: 1180px) {
  .app-shell {
    height: auto;
    min-height: 100vh;
    overflow: visible;
  }
  .workspace {
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "map map"
      "left ai";
  }
  .col-left {
    overflow: visible;
  }
  .col-map {
    height: 52vh;
    min-height: 380px;
  }
}

/* 手机：单列堆叠 */
@media (max-width: 760px) {
  .workspace {
    grid-template-columns: 1fr;
    grid-template-areas:
      "map"
      "left"
      "ai";
  }
  .col-map {
    height: 44vh;
    min-height: 300px;
  }
}
</style>
