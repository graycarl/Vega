"""
Vega Gateway - FastAPI 应用入口

LLM API Gateway 网关系统主应用，提供：
- 网关代理 API (/v1/*)
- Admin Console API (/api/*)
- 健康检查 (/health)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
import logging
import structlog
from src.config import settings

# 配置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(message)s",
)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("startup", message="Vega Gateway starting up")
    # TODO: 初始化数据库连接、HTTP 客户端等
    yield
    logger.info("shutdown", message="Vega Gateway shutting down")
    # TODO: 关闭资源

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="LLM API Gateway - 统一的 LLM API 网关，提供代理、限流、配置管理和用量统计",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    健康检查端点
    
    Returns:
        dict: 包含状态和时间戳的响应
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "vega-gateway",
        "version": "0.1.0",
    }


@app.get("/")
async def root() -> dict[str, str]:
    """
    根路径，返回 API 信息
    """
    return {
        "message": "Vega Gateway API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
