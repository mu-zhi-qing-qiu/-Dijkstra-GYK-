import os

from openai import OpenAI

from app.models.chat import ChatRequest, ChatResponse

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


class ChatService:
    """封装 DeepSeek 对话接口，API Key 从环境变量（.env）读取。"""

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        """惰性创建客户端，未配置 Key 时给出明确报错。"""
        if self._client is None:
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("未配置 DEEPSEEK_API_KEY，请在 .env 文件中设置后重试")
            self._client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
        return self._client

    def chat(self, request: ChatRequest) -> ChatResponse:
        client = self._get_client()
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.message},
            ],
            stream=False,
            reasoning_effort=request.reasoning_effort,
            extra_body={"thinking": {"type": "enabled"}},
        )

        message = response.choices[0].message
        return ChatResponse(
            content=message.content or "",
            reasoning_content=getattr(message, "reasoning_content", None),
            model=response.model,
        )
