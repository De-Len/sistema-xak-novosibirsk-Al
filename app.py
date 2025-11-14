import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from config import Config
from src.core.entities import QueryRequest, LLMResponse
from src.main import QuerySystem
from starlette.responses import HTMLResponse
from img.html_img import html_img

# Аутентификация по API ключу
API_KEY = Config.API_KEY
api_key_header = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


app = FastAPI(title="RAG API", version="1.0")
MAX_WORKERS = min(32, (os.cpu_count() or 1) * 2 + 1)
thread_pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)

query_system = QuerySystem()
# Единственный endpoint
@app.post("/query")
async def query_rag(
        request: QueryRequest,
        api_key: bool = Depends(check_api_key)
) -> LLMResponse:
    """Асинхронный запрос к RAG-системе"""

    try:
        return await query_system.query(request)

    except Exception as e:
        # Обработка ошибок
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "It's me, Gordei!",
        "time": datetime.now().isoformat(),
        "thread_pool_workers": MAX_WORKERS,
        "async": True
    }


@app.get("/")
async def show_image():
    """Показывает картинку по ссылке"""
    html_content = html_img
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)