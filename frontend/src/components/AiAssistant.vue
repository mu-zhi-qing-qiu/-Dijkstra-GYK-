<script setup>
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from "vue";
import { fetchChat } from "../api.js";
import { approxMinutes } from "../utils.js";

const props = defineProps({
  result: { type: Object, default: null },
  mode: { type: String, required: true },
  period: { type: String, required: true },
  start: { type: Object, required: true },
  end: { type: Object, required: true },
});

const messages = ref([]); // { role, content, reasoning, thinking, typing, error, showReason }
const generating = ref(false);
const scrollBox = ref(null);

let typeToken = 0;
let typeTimer = null;

const hasChat = computed(() => messages.value.length > 0);
const canGenerate = computed(() => !!props.result && !generating.value);

function scrollToBottom() {
  nextTick(() => {
    const el = scrollBox.value;
    if (el) el.scrollTop = el.scrollHeight;
  });
}

function modeText() {
  return props.mode === "walk" ? "步行" : "自行车";
}
function periodText() {
  const map = {
    normal: "普通时段",
    morning_peak: "早高峰",
    lunch_peak: "午高峰",
    evening_peak: "晚高峰",
  };
  return map[props.period] || props.period;
}

function buildPrompt() {
  const r = props.result;
  const names = r.path_names || [];
  const message = `请根据以下校园导航数据，生成一段自然、流畅、口语化的中文导航说明。
出行方式：${modeText()}
时段：${periodText()}
途经节点（按先后顺序）：${names.join(" → ")}
总距离：${Math.round(r.distance)} 米
预计耗时：约 ${approxMinutes(r.time)} 分钟（${Math.round(r.time)} 秒）

要求：
1. 用一段话描述如何从起点走到终点，自然地提到途经的主要地点；
2. 结合出行方式与时段给出贴心提示（如早高峰人多需提前出发、骑行注意减速慢行等）；
3. 结尾点明预计耗时；
4. 不要使用 Markdown，不要分点列表，控制在 120 字以内。`;
  const system_prompt =
    "你是「校园智航」智能导航助手，擅长把路径节点数据转写成亲切、专业、易懂的中文步行/骑行导航播报。语气友好、简洁、口语化。";
  return { message, system_prompt };
}

function userSummary() {
  return `请为我讲解 ${props.start.name} → ${props.end.name}（${modeText()} · ${periodText()}）的推荐路线`;
}

function typewriter(msg, fullText) {
  const token = ++typeToken;
  clearTimeout(typeTimer);
  msg.thinking = false;
  msg.typing = true;
  msg.content = "";
  let i = 0;
  const step = () => {
    if (token !== typeToken) return;
    i += 2;
    msg.content = fullText.slice(0, i);
    scrollToBottom();
    if (i < fullText.length) {
      typeTimer = setTimeout(step, 16);
    } else {
      msg.content = fullText;
      msg.typing = false;
    }
  };
  step();
}

async function generate(isRegenerate = false) {
  if (!canGenerate.value) return;
  generating.value = true;

  if (isRegenerate) {
    // 移除上一条助手回复，保留用户问题
    for (let i = messages.value.length - 1; i >= 0; i--) {
      if (messages.value[i].role === "assistant") {
        messages.value.splice(i, 1);
        break;
      }
    }
  } else {
    messages.value.push(reactive({ role: "user", content: userSummary() }));
  }

  const assistant = reactive({
    role: "assistant",
    content: "",
    reasoning: "",
    thinking: true,
    typing: false,
    error: false,
    showReason: false,
  });
  messages.value.push(assistant);
  scrollToBottom();

  try {
    const { message, system_prompt } = buildPrompt();
    const data = await fetchChat({ message, system_prompt });
    assistant.reasoning = data.reasoning_content || "";
    typewriter(assistant, data.content || "（未返回内容）");
  } catch (e) {
    assistant.thinking = false;
    assistant.error = true;
    assistant.content = e.message || "AI 服务暂时不可用，请稍后再试。";
    scrollToBottom();
  } finally {
    generating.value = false;
  }
}

function resetChat() {
  typeToken++;
  clearTimeout(typeTimer);
  messages.value = [];
  generating.value = false;
}

// 路线变化（出行方式/时段切换）时清空旧的 AI 说明，避免与新路线不一致
watch(() => props.result, resetChat);

onBeforeUnmount(() => {
  typeToken++;
  clearTimeout(typeTimer);
});
</script>

<template>
  <div class="ai glass anim-rise">
    <!-- 头部 -->
    <header class="ai-head">
      <div class="ai-avatar">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none">
          <path d="M12 3v3m0 12v3M5 12H2m20 0h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          <rect x="6" y="6" width="12" height="12" rx="4" stroke="currentColor" stroke-width="1.6" />
          <circle cx="9.5" cy="12" r="1.2" fill="currentColor" />
          <circle cx="14.5" cy="12" r="1.2" fill="currentColor" />
        </svg>
      </div>
      <div class="ai-id">
        <strong>AI 导航助手</strong>
        <span><i class="live"></i>智能讲解路线 · DeepSeek 驱动</span>
      </div>
      <button v-if="hasChat" class="icon-btn" title="清空对话" @click="resetChat">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
          <path d="M4 7h16M9 7V5h6v2m-8 0 1 13h8l1-13" stroke="currentColor"
            stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </button>
    </header>

    <!-- 对话区 -->
    <div class="ai-body" ref="scrollBox">
      <!-- 空态 -->
      <div v-if="!hasChat" class="ai-empty">
        <div class="orb"><span></span><span></span><span></span></div>
        <p class="ae-title">让 AI 为你讲解这条路线</p>
        <p class="ae-desc">
          点击下方按钮，把路径节点自动转换为自然语言导航播报，支持随时重新生成。
        </p>
        <div class="ae-tags">
          <span># 自然语言导航</span>
          <span># 贴心提示</span>
          <span># 流式生成</span>
        </div>
      </div>

      <!-- 消息列表 -->
      <template v-else>
        <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
          <div v-if="m.role === 'assistant'" class="m-avatar">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none">
              <path d="m12 3 2.1 4.9L19 10l-4.9 2.1L12 17l-2.1-4.9L5 10l4.9-2.1L12 3Z"
                fill="currentColor" />
            </svg>
          </div>
          <div class="bubble" :class="{ error: m.error }">
            <!-- 思考中 -->
            <div v-if="m.thinking" class="thinking">
              <span class="td"></span><span class="td"></span><span class="td"></span>
              <em>正在思考路线讲解…</em>
            </div>
            <!-- 内容 -->
            <template v-else>
              <p class="m-text">
                {{ m.content }}<span v-if="m.typing" class="caret"></span>
              </p>
              <!-- 思考过程 -->
              <div v-if="m.reasoning && !m.error" class="reason">
                <button class="reason-toggle" @click="m.showReason = !m.showReason">
                  <svg viewBox="0 0 24 24" width="13" height="13" fill="none"
                    :style="{ transform: m.showReason ? 'rotate(90deg)' : 'none' }">
                    <path d="m9 6 6 6-6 6" stroke="currentColor" stroke-width="1.8"
                      stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  思考过程
                </button>
                <p v-if="m.showReason" class="reason-text">{{ m.reasoning }}</p>
              </div>
            </template>
          </div>
        </div>
      </template>
    </div>

    <!-- 操作区 -->
    <footer class="ai-foot">
      <p v-if="!result" class="foot-hint">请先获取导航结果，再生成 AI 说明</p>
      <div class="foot-actions">
        <button
          v-if="!hasChat"
          class="btn btn-ai full"
          :disabled="!canGenerate"
          @click="generate(false)"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
            <path d="m12 3 2.1 4.9L19 10l-4.9 2.1L12 17l-2.1-4.9L5 10l4.9-2.1L12 3ZM19 16l.7 1.8L21.5 18l-1.8.7L19 21l-.7-2.3L16.5 18l1.8-.2L19 16Z"
              fill="currentColor" />
          </svg>
          生成 AI 导航说明
        </button>
        <button
          v-else
          class="btn full regen"
          :disabled="!canGenerate"
          @click="generate(true)"
        >
          <span v-if="generating" class="spinner"></span>
          <svg v-else viewBox="0 0 24 24" width="15" height="15" fill="none">
            <path d="M20 11a8 8 0 1 0-2.3 5.7M20 11V5m0 6h-6" stroke="currentColor"
              stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          {{ generating ? "生成中…" : "重新生成" }}
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.ai {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部 */
.ai-head {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 15px 16px;
  border-bottom: 1px solid var(--stroke);
  flex-shrink: 0;
}
.ai-avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: #0c0820;
  background: var(--grad-ai);
  box-shadow: var(--glow-violet);
}
.ai-id {
  flex: 1;
  min-width: 0;
}
.ai-id strong {
  display: block;
  font-size: 14.5px;
  font-weight: 700;
}
.ai-id span {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-2);
}
.ai-id .live {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--violet);
  box-shadow: 0 0 8px var(--violet);
  animation: pulse-dot 1.8s ease-in-out infinite;
}
.icon-btn {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  border: 1px solid var(--stroke);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
  cursor: pointer;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}
.icon-btn:hover {
  color: var(--rose);
  border-color: rgba(251, 113, 133, 0.4);
  background: rgba(251, 113, 133, 0.08);
}

/* 对话区 */
.ai-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 空态 */
.ai-empty {
  margin: auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
}
.orb {
  position: relative;
  width: 74px;
  height: 74px;
  display: grid;
  place-items: center;
  margin-bottom: 6px;
}
.orb span {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1.5px solid transparent;
}
.orb span:nth-child(1) {
  border-top-color: var(--violet);
  border-right-color: var(--violet);
  animation: spin 2.4s linear infinite;
}
.orb span:nth-child(2) {
  inset: 12px;
  border-bottom-color: var(--cyan);
  border-left-color: var(--cyan);
  animation: spin 1.8s linear infinite reverse;
}
.orb span:nth-child(3) {
  inset: 26px;
  border-radius: 50%;
  border: none;
  background: var(--grad-ai);
  box-shadow: var(--glow-violet);
  animation: pulse-dot 2s ease-in-out infinite;
}
.ae-title {
  font-size: 15px;
  font-weight: 700;
}
.ae-desc {
  font-size: 12.5px;
  line-height: 1.65;
  color: var(--text-2);
  max-width: 260px;
}
.ae-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  justify-content: center;
  margin-top: 4px;
}
.ae-tags span {
  font-size: 10.5px;
  padding: 4px 10px;
  border-radius: 99px;
  color: var(--text-1);
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

/* 消息 */
.msg {
  display: flex;
  gap: 9px;
  max-width: 100%;
  animation: rise 0.35s ease both;
}
.msg.user {
  justify-content: flex-end;
}
.m-avatar {
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: 8px;
  color: #0c0820;
  background: var(--grad-ai);
  margin-top: 2px;
}
.bubble {
  max-width: 84%;
  padding: 11px 14px;
  border-radius: 15px;
  font-size: 13.5px;
  line-height: 1.7;
}
.msg.assistant .bubble {
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid var(--stroke);
  border-top-left-radius: 5px;
  color: var(--text-0);
}
.msg.user .bubble {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.22), rgba(99, 102, 241, 0.22));
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-top-right-radius: 5px;
  color: var(--text-0);
}
.bubble.error {
  background: rgba(251, 113, 133, 0.1);
  border-color: rgba(251, 113, 133, 0.3);
  color: #ffd7de;
}
.m-text {
  white-space: pre-wrap;
  word-break: break-word;
}

/* 打字光标 */
.caret {
  display: inline-block;
  width: 7px;
  height: 15px;
  margin-left: 2px;
  vertical-align: text-bottom;
  background: var(--cyan);
  border-radius: 1px;
  animation: pulse-dot 0.9s steps(2) infinite;
}

/* 思考中 */
.thinking {
  display: flex;
  align-items: center;
  gap: 6px;
}
.thinking .td {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--violet);
  animation: pulse-dot 1.1s ease-in-out infinite;
}
.thinking .td:nth-child(2) {
  animation-delay: 0.18s;
}
.thinking .td:nth-child(3) {
  animation-delay: 0.36s;
}
.thinking em {
  font-style: normal;
  font-size: 12px;
  color: var(--text-2);
  margin-left: 4px;
}

/* 思考过程 */
.reason {
  margin-top: 9px;
  border-top: 1px dashed var(--stroke-strong);
  padding-top: 8px;
}
.reason-toggle {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-2);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
}
.reason-toggle svg {
  transition: transform 0.2s;
}
.reason-text {
  margin-top: 7px;
  font-size: 11.5px;
  line-height: 1.6;
  color: var(--text-2);
  white-space: pre-wrap;
  max-height: 160px;
  overflow-y: auto;
  padding: 9px 11px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.2);
}

/* 操作区 */
.ai-foot {
  flex-shrink: 0;
  padding: 13px 16px;
  border-top: 1px solid var(--stroke);
}
.foot-hint {
  font-size: 11px;
  color: var(--text-2);
  text-align: center;
  margin-bottom: 9px;
}
.foot-actions {
  display: flex;
  gap: 10px;
}
.btn.full {
  flex: 1;
  padding: 12px;
}
.btn.regen {
  background: rgba(139, 92, 246, 0.12);
  border-color: rgba(139, 92, 246, 0.3);
  color: #d9ccff;
}
.btn.regen:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.2);
}
.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-top-color: var(--violet);
  animation: spin 0.7s linear infinite;
}
</style>
