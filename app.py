import os

from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from config import Config
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


app = FastAPI(title="Gordei's API", version="1.0")
MAX_WORKERS = min(32, (os.cpu_count() or 1) * 2 + 1)
thread_pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)

query_system = QuerySystem()
# Единственный endpoint
@app.post("/query")
async def query_rag(
        request: QueryRequest,
        api_key: bool = Depends(check_api_key)
) -> LLMResponse:
    """Асинхронный запрос к системе"""

    try:
        return await query_system.query(request)

    except Exception as e:
        # Обработка ошибок
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.post("/query-streaming")
async def query_rag_streaming(
        request: QueryRequest,
        api_key: bool = Depends(check_api_key)
):
    """Streaming запрос к системе"""
    from starlette.responses import StreamingResponse
    import json

    async def generate_stream():
        """Генерирует streaming response"""
        try:
            async for chunk in query_system.query_stream(request):
                # Формируем данные в формате Server-Sent Events (SSE)
                chunk_data = {
                    "content": chunk.content_chunk,
                    "chat_id": chunk.chat_id,
                    "is_completed": chunk.is_completed,
                    "question_count": chunk.question_count,
                    "total_questions": chunk.total_questions,
                    "is_final_chunk": chunk.is_final_chunk
                }

                # Отправляем chunk как SSE событие
                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"

                # Небольшая задержка для имитации "печатания" (опционально)
                await asyncio.sleep(0.01)

        except Exception as e:
            # В случае ошибки отправляем error event
            error_data = {
                "content": f"Error: {str(e)}",
                "chat_id": "",
                "is_completed": True,
                "question_count": 0,
                "total_questions": 0,
                "is_final_chunk": True,
                "error": True
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "X-API-Key, Content-Type",
        }
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