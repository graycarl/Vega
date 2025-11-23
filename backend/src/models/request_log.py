from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

def utc_now():
    return datetime.now(timezone.utc)

class RequestLog(BaseModel):
    """请求记录模型"""
    id: UUID = Field(default_factory=uuid4, description="请求唯一标识")
    server_id: UUID = Field(..., description="关联的后端服务器 ID")
    app_name: str = Field(..., min_length=1, max_length=100, description="客户端应用名称")
    model: str = Field(..., min_length=1, max_length=100, description="请求的模型名称")
    prompt_tokens: int = Field(default=0, ge=0, description="提示词 token 数")
    completion_tokens: int = Field(default=0, ge=0, description="生成内容 token 数")
    total_tokens: int = Field(default=0, ge=0, description="总 token 数")
    status_code: int = Field(..., ge=200, le=599, description="HTTP 响应状态码")
    latency_ms: int = Field(..., ge=0, description="请求延迟（毫秒）")
    is_queued: bool = Field(default=False, description="是否曾进入队列")
    queue_wait_ms: Optional[int] = Field(default=None, description="队列等待时间（毫秒）")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    timestamp: datetime = Field(default_factory=utc_now, description="请求时间戳")

    def calculate_total_tokens(self) -> None:
        """计算总 token 数"""
        self.total_tokens = self.prompt_tokens + self.completion_tokens
