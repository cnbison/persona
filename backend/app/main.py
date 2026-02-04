"""
FastAPI应用入口
Persona生成与应用平台 - 后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.utils.config import settings
from app.api import health, books, personas, outlines, scripts, audiences, outputs

# 配置日志
logger.remove()  # 移除默认handler
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO"
)

# 创建FastAPI应用
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="Persona生成与应用平台 - 后端API服务",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境需限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"🚀 {settings.project_name} v{settings.project_version} 启动中...")
    logger.info(f"📝 OpenAI模型: {settings.openai_model}")
    logger.info(f"📚 著作目录: {settings.books_dir}")
    logger.info(f"💾 数据库: {settings.database_url}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("👋 应用关闭")


# 注册API路由
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(books.router, prefix="/api/books", tags=["著作管理"])
app.include_router(personas.router, prefix="/api/personas", tags=["Persona管理"])
app.include_router(audiences.router, prefix="/api/audiences", tags=["受众Persona"])
app.include_router(outlines.router, prefix="/api/outlines", tags=["提纲管理"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["脚本管理"])
app.include_router(outputs.router, prefix="/api/outputs", tags=["输出与诊断"])


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Persona生成与应用平台 API",
        "version": settings.project_version,
        "docs": "/docs",
        "status": "running"
    }


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"❌ 未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.debug else "请联系管理员"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
