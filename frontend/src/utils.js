// 场景常量与通用格式化工具

// 示例场景：仅「桃蹊饭堂(C2) → 格致楼(S1)」的普通/早高峰时段有预绘制路线图
export const EXAMPLE = { startId: 35, endId: 22 };

export const MODES = [
  { value: "walk", label: "步行", desc: "环保慢行", grad: "var(--grad-walk)" },
  { value: "bike", label: "自行车", desc: "快速通勤", grad: "var(--grad-bike)" },
];

// 时段与后端 PERIOD_FACTORS 对齐：normal / morning_peak / lunch_peak / evening_peak
export const PERIODS = [
  { value: "normal", label: "普通时段", desc: "道路通畅", level: "low" },
  { value: "morning_peak", label: "早高峰", desc: "上课人流", level: "high" },
  { value: "lunch_peak", label: "午高峰", desc: "饭点拥堵", level: "mid" },
  { value: "evening_peak", label: "晚高峰", desc: "放学高峰", level: "high" },
];

/** 仅示例场景的普通/早高峰才有预绘制路线图 */
export function hasDrawnRoute(startId, endId, period) {
  return (
    startId === EXAMPLE.startId &&
    endId === EXAMPLE.endId &&
    (period === "normal" || period === "morning_peak")
  );
}

export const BASE_MAP = "/assets/maps/campus-map.jpg";

/** 当前应展示的地图图层：示例场景显示路线图，其余显示不画路线的普通地图 */
export function mapLayer(startId, endId, mode, period) {
  if (!hasDrawnRoute(startId, endId, period)) return BASE_MAP;
  const p = period === "morning_peak" ? "morning-peak" : "normal";
  return `/assets/routes/${mode}-${p}.png`;
}

/** 距离格式化：米 / 公里 */
export function formatDistance(meters) {
  if (meters == null) return "—";
  if (meters >= 1000) return `${(meters / 1000).toFixed(2)} km`;
  return `${Math.round(meters)} m`;
}

/** 耗时格式化：秒 → X 分 Y 秒 */
export function formatDuration(seconds) {
  if (seconds == null) return "—";
  const total = Math.round(seconds);
  const m = Math.floor(total / 60);
  const s = total % 60;
  if (m <= 0) return `${s} 秒`;
  if (s === 0) return `${m} 分钟`;
  return `${m} 分 ${s} 秒`;
}

/** 约耗时（分钟） */
export function approxMinutes(seconds) {
  return Math.max(1, Math.round((seconds || 0) / 60));
}

/** 规则化的简明文字导航说明（与 AI 自然语言版本互补） */
export function buildTextGuide(result, mode) {
  if (!result || !result.path_names || result.path_names.length === 0) return "";
  const names = result.path_names;
  const modeText = mode === "walk" ? "步行" : "骑行";
  if (names.length === 1) return `起点与终点相同（${names[0]}），无需移动。`;
  const via = names.slice(1, -1);
  let s = `${modeText}从「${names[0]}」出发`;
  if (via.length) s += `，依次经过 ${via.map((n) => `「${n}」`).join("、")}`;
  s += `，最终抵达「${names[names.length - 1]}」。`;
  s += `全程约 ${formatDistance(result.distance)}，预计耗时 ${formatDuration(result.time)}。`;
  return s;
}
