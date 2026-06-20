from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.navigation import router as navigation_router

# 在创建应用前加载 .env，使 DEEPSEEK_API_KEY 等环境变量可用。
load_dotenv()

app = FastAPI(
    title="Campus Navigation System",
    description="Campus navigation API with Dijkstra and Floyd shortest path endpoints.",
    version="1.0.0",
)

app.include_router(navigation_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
