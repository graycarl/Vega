from datetime import datetime, timezone
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

def utc_now():
    return datetime.now(timezone.utc)

class BucketType(str, Enum):
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"

class UsageStats(BaseModel):
    """用量统计预聚合模型"""
    server_id: UUID = Field(..., description="后端服务器 ID")
    app_name: str = Field(..., min_length=1, max_length=100, description="客户端应用名称")
    time_bucket: str = Field(..., max_length=20, description="时间分组")
    bucket_type: BucketType = Field(..., description="时间粒度")
    total_requests: int = Field(default=0, ge=0, description="总请求数")
    successful_requests: int = Field(default=0, ge=0, description="成功请求数")
    failed_requests: int = Field(default=0, ge=0, description="失败请求数")
    total_tokens: int = Field(default=0, ge=0, description="总 token 数")
    avg_latency_ms: float = Field(default=0.0, ge=0.0, description="平均延迟（毫秒）")
    queued_requests: int = Field(default=0, ge=0, description="曾排队的请求数")
    updated_at: datetime = Field(default_factory=utc_now, description="最后更新时间")
