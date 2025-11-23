from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """应用配置"""
    # 基础配置
    APP_NAME: str = "Vega Gateway"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///data/gateway.db"
    
    # 安全配置
    VEGA_SECRET_KEY: Optional[str] = None  # 用于加密 API Key
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost"]
    
    # 网关配置
    HTTP_TIMEOUT: int = 30
    MAX_CONNECTIONS: int = 200
    MAX_KEEPALIVE: int = 50

    class Config:
        env_file = ".env"

settings = Settings()
