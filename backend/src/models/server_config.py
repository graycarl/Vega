from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl, field_validator

def utc_now():
    return datetime.now(timezone.utc)

class ServerConfig(BaseModel):
    """后端服务器配置模型"""
    id: UUID = Field(default_factory=uuid4, description="服务器唯一标识")
    name: str = Field(..., min_length=1, max_length=100, description="服务器名称")
    url: HttpUrl = Field(..., description="后端 API 基础 URL")
    api_key: str = Field(..., min_length=1, max_length=200, description="后端服务器 API Key")
    models: List[str] = Field(..., min_length=1, description="支持的模型列表")
    rpm_limit: int = Field(..., ge=0, description="每分钟请求数限制（0 表示无限制）")
    tpm_limit: int = Field(..., ge=0, description="每分钟 token 数限制（0 表示无限制）")
    queue_max_size: int = Field(default=100, gt=0, description="队列最大长度")
    queue_timeout_seconds: int = Field(default=30, gt=0, description="队列超时时间（秒）")
    is_active: bool = Field(default=True, description="是否启用该服务器")
    created_at: datetime = Field(default_factory=utc_now, description="创建时间")
    updated_at: datetime = Field(default_factory=utc_now, description="最后更新时间")

    @field_validator('url')
    @classmethod
    def validate_url_scheme(cls, v: HttpUrl) -> HttpUrl:
        if v.scheme != 'https':
            raise ValueError('URL must be HTTPS')
        return v

    @field_validator('tpm_limit')
    @classmethod
    def validate_limits(cls, v: int, info) -> int:
        values = info.data
        if 'rpm_limit' in values and values['rpm_limit'] == 0 and v == 0:
            raise ValueError('rpm_limit and tpm_limit cannot both be 0')
        return v
