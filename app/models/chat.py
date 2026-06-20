from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户输入的消息")
    system_prompt: str = Field("You are a helpful assistant", description="系统提示词")
    model: str = Field("deepseek-v4-pro", description="DeepSeek 模型名称")
    reasoning_effort: str = Field("high", description="推理强度: low / medium / high")


class ChatResponse(BaseModel):
    content: str = Field(..., description="模型回复内容")
    reasoning_content: str | None = Field(None, description="模型思考过程（开启 thinking 时返回）")
    model: str = Field(..., description="实际使用的模型名称")
