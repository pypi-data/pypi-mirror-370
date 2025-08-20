import os
import logging
from fastapi import APIRouter
from fastapi.responses import FileResponse

web_router = APIRouter()

class StaticAccessFilter(logging.Filter):
    def filter(self, record):
        # 屏蔽所有 FastAPI 的访问日志（GET 请求）
        return "GET /" not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(StaticAccessFilter())

# 前端静态文件目录
DIST_DIR = os.path.join(os.path.dirname(__file__), "client")

@web_router.get("/web/{full_path:path}", include_in_schema=False)
async def serve_static(full_path: str):
    # 如果请求的是根路径，返回 index.html
    if not full_path or full_path == "/":
        return FileResponse(os.path.join(DIST_DIR, "index.html"))

    # 检查请求路径是否为静态文件
    file_path = os.path.join(DIST_DIR, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # 如果路径不存在，返回 index.html（适配前端 SPA 路由）
    return FileResponse(os.path.join(DIST_DIR, "index.html"))
