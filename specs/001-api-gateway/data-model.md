# 数据模型设计 - LLM API Gateway

**日期**: 2025-11-23  
**目的**: 定义系统核心实体及其关系，指导数据库设计和代码实现

## 核心实体

### 1. ServerConfig (后端服务器配置)

**用途**: 存储 LLM 后端服务器的连接和限流配置

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 服务器唯一标识 |
| name | String(100) | NOT NULL | 服务器名称（用于展示） |
| url | String(500) | NOT NULL, UNIQUE | 后端 API 基础 URL（如 https://api.openai.com/v1） |
| api_key | String(200) | NOT NULL | 后端服务器的 API Key（加密存储） |
| models | JSON Array | NOT NULL | 支持的模型列表，如 ["gpt-4", "gpt-3.5-turbo"] |
| rpm_limit | Integer | NOT NULL, >= 0 | 每分钟请求数限制（0 表示无限制） |
| tpm_limit | Integer | NOT NULL, >= 0 | 每分钟 token 数限制（0 表示无限制） |
| queue_max_size | Integer | NOT NULL, DEFAULT 100 | 队列最大长度 |
| queue_timeout_seconds | Integer | NOT NULL, DEFAULT 30 | 队列超时时间（秒） |
| is_active | Boolean | NOT NULL, DEFAULT true | 是否启用该服务器 |
| created_at | DateTime | NOT NULL | 创建时间 |
| updated_at | DateTime | NOT NULL | 最后更新时间 |

**验证规则**:
- `url` 必须是有效的 HTTPS URL
- `rpm_limit` 和 `tpm_limit` 不能同时为 0
- `models` 数组不能为空
- `queue_max_size` 必须 > 0
- `api_key` 在存储前使用 Fernet 加密

**关系**:
- 一对多 -> RequestLog（一个服务器对应多条请求记录）
- 一对多 -> UsageStats（一个服务器对应多条统计记录）

---

### 2. RequestLog (请求记录)

**用途**: 记录每次通过网关的 API 调用，用于用量统计和审计

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 请求唯一标识 |
| server_id | UUID | NOT NULL, FOREIGN KEY | 关联的后端服务器 ID |
| app_name | String(100) | NOT NULL | 客户端应用名称（从 header 提取） |
| model | String(100) | NOT NULL | 请求的模型名称 |
| prompt_tokens | Integer | NOT NULL, DEFAULT 0 | 提示词 token 数 |
| completion_tokens | Integer | NOT NULL, DEFAULT 0 | 生成内容 token 数 |
| total_tokens | Integer | NOT NULL, DEFAULT 0 | 总 token 数 |
| status_code | Integer | NOT NULL | HTTP 响应状态码 |
| latency_ms | Integer | NOT NULL | 请求延迟（毫秒） |
| is_queued | Boolean | NOT NULL, DEFAULT false | 是否曾进入队列 |
| queue_wait_ms | Integer | DEFAULT NULL | 队列等待时间（毫秒，未排队则为 NULL） |
| error_message | Text | DEFAULT NULL | 错误信息（成功则为 NULL） |
| timestamp | DateTime | NOT NULL, INDEX | 请求时间戳 |

**验证规则**:
- `total_tokens` = `prompt_tokens` + `completion_tokens`
- `status_code` 在 200-599 之间
- `latency_ms` >= 0

**索引**:
- `(server_id, app_name, timestamp)`: 用于用量统计查询
- `(timestamp)`: 用于时间范围查询
- `(server_id, timestamp)`: 用于按服务器查询

**关系**:
- 多对一 -> ServerConfig（多条请求属于一个服务器）

---

### 3. UsageStats (用量统计预聚合)

**用途**: 预聚合的用量统计数据，提高查询性能

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| server_id | UUID | NOT NULL, FOREIGN KEY | 后端服务器 ID |
| app_name | String(100) | NOT NULL | 客户端应用名称 |
| time_bucket | String(20) | NOT NULL | 时间分组（如 "2025-11-23T14" 表示某小时） |
| bucket_type | Enum | NOT NULL | 时间粒度：hour, day, month |
| total_requests | Integer | NOT NULL, DEFAULT 0 | 总请求数 |
| successful_requests | Integer | NOT NULL, DEFAULT 0 | 成功请求数（2xx 状态码） |
| failed_requests | Integer | NOT NULL, DEFAULT 0 | 失败请求数（4xx/5xx 状态码） |
| total_tokens | BigInteger | NOT NULL, DEFAULT 0 | 总 token 数 |
| avg_latency_ms | Float | NOT NULL, DEFAULT 0 | 平均延迟（毫秒） |
| queued_requests | Integer | NOT NULL, DEFAULT 0 | 曾排队的请求数 |
| updated_at | DateTime | NOT NULL | 最后更新时间 |

**主键**: `(server_id, app_name, time_bucket, bucket_type)`

**验证规则**:
- `total_requests` = `successful_requests` + `failed_requests`
- `bucket_type` 必须是 "hour", "day", "month" 之一

**索引**:
- `(server_id, time_bucket, bucket_type)`: 按服务器查询
- `(app_name, time_bucket, bucket_type)`: 按应用查询

**关系**:
- 多对一 -> ServerConfig（多条统计属于一个服务器）

---

### 4. QueueItem (队列项 - 仅内存)

**用途**: 运行时队列中的请求项（不持久化到数据库）

**字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| request_id | UUID | 唯一标识 |
| server_id | UUID | 目标后端服务器 |
| app_name | String | 客户端应用名称 |
| http_request | Object | 原始 HTTP 请求对象（包含 method, path, headers, body） |
| enqueued_at | DateTime | 入队时间 |
| estimated_tokens | Integer | 预估 token 数（用于 TPM 限流判断） |

**存储**: 使用 `asyncio.Queue`，重启时丢失

**生命周期**:
1. 请求超限时创建 QueueItem 并入队
2. 限流窗口重置后，从队列取出并处理
3. 处理完成或超时后销毁

---

## 实体关系图

```text
┌─────────────────┐
│  ServerConfig   │
│  (服务器配置)    │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────┐
    │                          │
    ▼                          ▼
┌──────────┐            ┌──────────────┐
│RequestLog│            │ UsageStats   │
│(请求记录) │            │ (用量统计)    │
└──────────┘            └──────────────┘
    │
    │ 聚合
    │
    └──────────────────▶ (定时任务生成)
```

---

## 状态转换

### 请求处理流程状态

```text
[客户端请求]
    │
    ▼
[验证 App-Name] ──失败──▶ [返回 400]
    │ 成功
    ▼
[选择服务器] ──无可用──▶ [返回 404]
    │ 找到
    ▼
[检查限流]
    │
    ├──未超限──▶ [直接转发] ──▶ [记录日志] ──▶ [返回响应]
    │
    └──超限──▶ [入队] ──▶ [等待]
                 │          │
                 │          ├──超时──▶ [返回 504]
                 │          │
                 │          └──窗口重置──▶ [出队转发] ──▶ [记录日志] ──▶ [返回响应]
                 │
                 └──队列满──▶ [驱逐最旧] ──▶ [被驱逐请求返回 503]
```

---

## 数据一致性保证

### 配置变更

- Admin API 修改配置时，立即写入数据库
- 网关服务每 5 秒重新加载配置（`reload_config_periodically`）
- 正在处理的请求使用已加载的配置快照，不受变更影响

### 用量统计

- 每次请求完成时，立即写入 `RequestLog` 表
- 后台任务每分钟扫描 `RequestLog`，聚合数据到 `UsageStats`
- 聚合时使用 `INSERT OR REPLACE` 保证幂等性

### 队列持久化

- 队列不持久化，网关重启时队列清空
- 队列中的请求在重启时会丢失（符合规格说明的边界情况）
- 可通过健康检查避免在处理请求时重启

---

## Pydantic 模型映射

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4

class ServerConfigCreate(BaseModel):
    """创建服务器配置的请求模型"""
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., regex=r'^https://.+')
    api_key: str = Field(..., min_length=1)
    models: List[str] = Field(..., min_items=1)
    rpm_limit: int = Field(..., ge=0)
    tpm_limit: int = Field(..., ge=0)
    queue_max_size: int = Field(default=100, gt=0)
    queue_timeout_seconds: int = Field(default=30, gt=0)
    
    @validator('rpm_limit', 'tpm_limit')
    def check_limits(cls, v, values):
        # rpm 和 tpm 不能同时为 0
        if v == 0 and values.get('rpm_limit') == 0:
            raise ValueError('rpm_limit 和 tpm_limit 不能同时为 0')
        return v

class ServerConfigResponse(BaseModel):
    """服务器配置的响应模型"""
    id: UUID
    name: str
    url: str
    models: List[str]
    rpm_limit: int
    tpm_limit: int
    queue_max_size: int
    queue_timeout_seconds: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # 支持从 ORM 对象创建

class RequestLogCreate(BaseModel):
    """创建请求日志的内部模型"""
    server_id: UUID
    app_name: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    status_code: int
    latency_ms: int
    is_queued: bool = False
    queue_wait_ms: Optional[int] = None
    error_message: Optional[str] = None
    
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

class UsageStatsResponse(BaseModel):
    """用量统计的响应模型"""
    server_id: UUID
    app_name: str
    time_bucket: str
    bucket_type: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    avg_latency_ms: float
    queued_requests: int
```

---

## 数据库 Schema (SQLite)

```sql
-- 服务器配置表
CREATE TABLE server_configs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    api_key TEXT NOT NULL,  -- 加密存储
    models TEXT NOT NULL,   -- JSON 数组字符串
    rpm_limit INTEGER NOT NULL DEFAULT 0,
    tpm_limit INTEGER NOT NULL DEFAULT 0,
    queue_max_size INTEGER NOT NULL DEFAULT 100,
    queue_timeout_seconds INTEGER NOT NULL DEFAULT 30,
    is_active INTEGER NOT NULL DEFAULT 1,  -- SQLite 用整数表示布尔值
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 请求日志表
CREATE TABLE request_logs (
    id TEXT PRIMARY KEY,
    server_id TEXT NOT NULL,
    app_name TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    status_code INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    is_queued INTEGER NOT NULL DEFAULT 0,
    queue_wait_ms INTEGER,
    error_message TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (server_id) REFERENCES server_configs(id) ON DELETE CASCADE
);

CREATE INDEX idx_request_logs_stats ON request_logs(server_id, app_name, timestamp);
CREATE INDEX idx_request_logs_timestamp ON request_logs(timestamp);

-- 用量统计表
CREATE TABLE usage_stats (
    server_id TEXT NOT NULL,
    app_name TEXT NOT NULL,
    time_bucket TEXT NOT NULL,
    bucket_type TEXT NOT NULL CHECK(bucket_type IN ('hour', 'day', 'month')),
    total_requests INTEGER NOT NULL DEFAULT 0,
    successful_requests INTEGER NOT NULL DEFAULT 0,
    failed_requests INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    avg_latency_ms REAL NOT NULL DEFAULT 0.0,
    queued_requests INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (server_id, app_name, time_bucket, bucket_type),
    FOREIGN KEY (server_id) REFERENCES server_configs(id) ON DELETE CASCADE
);

CREATE INDEX idx_usage_stats_server ON usage_stats(server_id, time_bucket, bucket_type);
CREATE INDEX idx_usage_stats_app ON usage_stats(app_name, time_bucket, bucket_type);
```

---

## 总结

数据模型设计完成，涵盖：
- ✅ 4 个核心实体：ServerConfig, RequestLog, UsageStats, QueueItem
- ✅ 完整的字段定义、验证规则和关系
- ✅ 状态转换流程和一致性保证
- ✅ Pydantic 模型定义
- ✅ SQLite 数据库 Schema

**可进入 API 契约设计阶段。**
