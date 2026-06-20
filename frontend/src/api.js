// 统一的后端接口封装。开发环境通过 Vite 代理转发到 http://127.0.0.1:8000

/** 调用最短路径导航接口（Dijkstra） */
export async function fetchNavigation(payload) {
  const res = await fetch("/api/navigation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `导航接口异常 (HTTP ${res.status})`);
  }
  return res.json();
}

/** 调用 AI 对话接口（DeepSeek） */
export async function fetchChat(payload) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `AI 接口异常 (HTTP ${res.status})`);
  }
  return res.json();
}

/** 获取全部校园地点（用于起终点选择） */
export async function fetchPlaces() {
  const res = await fetch("/api/places", { method: "GET" });
  if (!res.ok) throw new Error(`地点列表获取失败 (HTTP ${res.status})`);
  return res.json();
}

/** 后端健康检查 */
export async function fetchHealth() {
  const res = await fetch("/health", { method: "GET" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
