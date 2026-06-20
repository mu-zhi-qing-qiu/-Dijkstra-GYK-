<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: Number, default: null },
  places: { type: Array, default: () => [] },
  accent: { type: String, default: "start" }, // start | end
  placeholder: { type: String, default: "选择地点" },
});
const emit = defineEmits(["update:modelValue"]);

const root = ref(null);
const searchInput = ref(null);
const open = ref(false);
const q = ref("");

const selected = computed(() => props.places.find((p) => p.id === props.modelValue) || null);

const filtered = computed(() => {
  const kw = q.value.trim().toLowerCase();
  if (!kw) return props.places;
  return props.places.filter(
    (p) => p.name.toLowerCase().includes(kw) || p.code.toLowerCase().includes(kw)
  );
});

function toggle() {
  open.value = !open.value;
  if (open.value) {
    q.value = "";
    nextTick(() => searchInput.value?.focus());
  }
}
function select(p) {
  emit("update:modelValue", p.id);
  open.value = false;
}
function onDocClick(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false;
}
function onKey(e) {
  if (e.key === "Escape") open.value = false;
}

watch(open, (v) => {
  if (v) {
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onKey);
  } else {
    document.removeEventListener("mousedown", onDocClick);
    document.removeEventListener("keydown", onKey);
  }
});
onBeforeUnmount(() => {
  document.removeEventListener("mousedown", onDocClick);
  document.removeEventListener("keydown", onKey);
});
</script>

<template>
  <div class="picker" ref="root">
    <button class="trigger" :class="{ open }" @click="toggle">
      <span class="pin" :class="accent"></span>
      <span class="val" :class="{ ph: !selected }">
        {{ selected ? selected.name : placeholder }}
      </span>
      <span class="code" v-if="selected">{{ selected.code }}</span>
      <svg class="chev" :class="{ flip: open }" viewBox="0 0 24 24" width="15" height="15" fill="none">
        <path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="1.7"
          stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <Transition name="pop">
      <div class="pop" v-if="open">
        <div class="search">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.6" />
            <path d="m20 20-3.2-3.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          </svg>
          <input ref="searchInput" v-model="q" type="text" placeholder="搜索地点名称或代码…" />
        </div>
        <ul class="list">
          <li
            v-for="p in filtered"
            :key="p.id"
            :class="{ active: p.id === modelValue }"
            @click="select(p)"
          >
            <span class="name">{{ p.name }}</span>
            <span class="lcode">{{ p.code }}</span>
          </li>
          <li v-if="filtered.length === 0" class="empty">未找到匹配地点</li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.picker {
  position: relative;
}
.trigger {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: var(--r-sm);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--stroke);
  color: var(--text-0);
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.trigger:hover,
.trigger.open {
  border-color: var(--stroke-strong);
  background: rgba(255, 255, 255, 0.06);
}
.pin {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.pin.start {
  background: var(--green);
  box-shadow: 0 0 9px var(--green);
}
.pin.end {
  background: var(--rose);
  box-shadow: 0 0 9px var(--rose);
}
.val {
  flex: 1;
  text-align: left;
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.val.ph {
  color: var(--text-2);
  font-weight: 500;
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
.chev {
  color: var(--text-2);
  transition: transform 0.25s;
}
.chev.flip {
  transform: rotate(180deg);
}

/* 下拉面板 */
.pop {
  position: absolute;
  z-index: 30;
  top: calc(100% + 7px);
  left: 0;
  right: 0;
  border-radius: var(--r-md);
  background: var(--surface-strong);
  backdrop-filter: blur(22px) saturate(160%);
  -webkit-backdrop-filter: blur(22px) saturate(160%);
  border: 1px solid var(--stroke-strong);
  box-shadow: var(--shadow-panel);
  overflow: hidden;
}
.search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 12px;
  border-bottom: 1px solid var(--stroke);
  color: var(--text-2);
}
.search input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--text-0);
  font-family: inherit;
  font-size: 13px;
}
.search input::placeholder {
  color: var(--text-2);
}
.list {
  list-style: none;
  max-height: 240px;
  overflow-y: auto;
  padding: 6px;
}
.list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 9px 11px;
  border-radius: 9px;
  cursor: pointer;
  transition: background 0.15s;
}
.list li:hover {
  background: rgba(34, 211, 238, 0.1);
}
.list li.active {
  background: rgba(34, 211, 238, 0.16);
}
.list li.active .name {
  color: var(--cyan);
}
.name {
  font-size: 13.5px;
  font-weight: 600;
}
.lcode {
  font-size: 10.5px;
  color: var(--text-2);
  font-variant-numeric: tabular-nums;
}
.empty {
  text-align: center;
  color: var(--text-2);
  font-size: 12.5px;
  cursor: default;
  padding: 16px;
}
.empty:hover {
  background: none;
}

/* 动画 */
.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
