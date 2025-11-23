# Phase 0: 技术调研 - LLM API Gateway

**日期**: 2025-11-23  
**目的**: 解决技术实现中的未知问题，为设计阶段提供决策依据

## 调研任务

### 1. FastAPI 异步请求代理最佳实践

**问题**: 如何使用 FastAPI + httpx 实现高性能的异步 HTTP 代理？

**决策**: 使用 httpx.AsyncClient 作为全局单例，配置连接池和超时参数

**理由**:
- httpx 是现代异步 HTTP 客户端，完全兼容 asyncio
- 全局 AsyncClient 复用连接池，避免每次请求创建新连接
- 支持 HTTP/2，性能优于 aiohttp
- 与 FastAPI 集成良好，类型提示完善

**替代方案考虑**:
- aiohttp: 功能类似但类型支持较弱，社区逐渐转向 httpx
- requests + threading: 非异步，无法满足高并发要求

**实现要点**:
```python
# 应用启动时创建全局客户端
app = FastAPI()
http_client = None

@app.on_event("startup")
async def startup():
    global http_client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=50)
    )

@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()
```

---

### 2. 限流算法选择：Sliding Window vs Token Bucket

**问题**: 实现 RPM 和 TPM 限流时，应该选择哪种算法？

**决策**: 使用 Sliding Window Counter 算法

**理由**:
- 适合分钟级窗口，内存占用小
- 计数精确，避免 Token Bucket 的突发流量问题
- 易于实现 TPM（token per minute）和 RPM（request per minute）
- 符合 OpenAI API 的限流行为

**替代方案考虑**:
- Token Bucket: 允许短时突发，但可能导致限流不准确
- Fixed Window: 窗口边界问题，容易被绕过
- Leaky Bucket: 平滑流量但复杂度高，不适合分钟级窗口

**实现要点**:
- 使用时间戳记录每个请求
- 每次检查时清理过期记录（超过 60 秒）
- 判断当前窗口内计数是否超限

---

### 3. 异步队列管理：asyncio.Queue vs 自定义实现

**问题**: 排队功能使用 asyncio.Queue 还是自定义队列？

**决策**: 使用 asyncio.Queue + maxsize 参数，结合 FIFO 驱逐逻辑

**理由**:
- asyncio.Queue 原生支持异步等待，无需自己实现锁
- maxsize 参数天然支持容量限制
- 需要额外实现 FIFO 驱逐：队列满时主动取出最旧元素

**替代方案考虑**:
- collections.deque + asyncio.Lock: 需要手动管理并发安全
- 第三方队列库（如 aio-pika）: 过度设计，引入额外依赖

**实现要点**:
```python
# 每个后端服务器一个队列
server_queues = {}  # server_id -> asyncio.Queue

async def enqueue_request(server_id, request):
    queue = server_queues[server_id]
    if queue.full():
        # FIFO 驱逐：移除最旧的请求
        await queue.get()
    await queue.put(request)
```

---

### 4. 配置动态加载机制

**问题**: 如何在不重启服务的情况下，让配置变更立即生效？

**决策**: 使用共享内存字典 + 文件监听机制（watchdog）

**理由**:
- 配置存储在 SQLite 中，Admin API 修改配置时更新数据库
- 网关服务定期（每 5 秒）重新加载配置到内存
- 使用 Python 字典作为配置缓存，读取操作无锁
- 正在处理的请求使用已加载的配置，不受变更影响

**替代方案考虑**:
- 信号机制（SIGHUP）: 需要手动触发，不符合"自动生效"需求
- 消息队列（Redis Pub/Sub）: 引入额外依赖，增加复杂度
- 数据库轮询: 每次请求都查数据库，性能差

**实现要点**:
```python
# 后台任务定期重新加载配置
@app.on_event("startup")
async def start_config_reloader():
    asyncio.create_task(reload_config_periodically())

async def reload_config_periodically():
    while True:
        await asyncio.sleep(5)  # 每 5 秒检查一次
        new_config = await load_config_from_db()
        global_config.update(new_config)
```

---

### 5. Vue.js 3 与 FastAPI 集成方式

**问题**: 前后端如何部署和通信？

**决策**: 开发环境前后端分离（Vite dev server + FastAPI），生产环境前端构建为静态文件由 nginx 服务

**理由**:
- 开发时 Vite 提供热重载，FastAPI 提供 CORS 支持
- 生产时前端打包为静态文件，nginx 高效服务静态资源
- 前后端通过 REST API 通信，使用 axios 调用后端

**替代方案考虑**:
- FastAPI 直接服务前端静态文件: 性能不如 nginx
- 服务端渲染（SSR）: 无必要，Admin Console 无 SEO 需求

**实现要点**:
- docker-compose 中配置两个服务：backend (FastAPI) + frontend (nginx)
- 开发环境：frontend Vite 代理 API 请求到 backend:8000
- 生产环境：nginx 反向代理 /api/* 到 backend:8000

---

### 6. SQLite 数据持久化方案

**问题**: SQLite 是否足够支持并发读写？

**决策**: 使用 aiosqlite（异步 SQLite）+ WAL 模式

**理由**:
- aiosqlite 提供异步接口，避免阻塞事件循环
- WAL（Write-Ahead Logging）模式支持并发读写
- 初期数据量小，SQLite 性能足够
- 后期可平滑迁移到 PostgreSQL（使用 SQLAlchemy 抽象层）

**替代方案考虑**:
- 直接使用 sqlite3: 同步操作会阻塞 asyncio
- PostgreSQL: 初期过度设计，增加运维成本

**实现要点**:
```python
import aiosqlite

async def init_db():
    async with aiosqlite.connect("gateway.db") as db:
        await db.execute("PRAGMA journal_mode=WAL")  # 启用 WAL
        await db.execute("""
            CREATE TABLE IF NOT EXISTS server_configs (...)
        """)
        await db.commit()
```

---

### 7. 用量统计聚合策略

**问题**: 如何高效聚合按"服务器+应用"维度的用量统计？

**决策**: 实时写入请求日志，定时聚合到统计表

**理由**:
- 每次请求写入 `request_logs` 表（包含 server_id, app_name, tokens, timestamp）
- 后台任务每分钟聚合数据到 `usage_stats` 表（按小时/天维度预聚合）
- 查询统计时从 `usage_stats` 表读取，性能高

**替代方案考虑**:
- 实时聚合: 每次查询都扫描所有日志，性能差
- 流式处理（Kafka + Flink）: 过度设计

**实现要点**:
```sql
-- 请求日志表
CREATE TABLE request_logs (
    id INTEGER PRIMARY KEY,
    server_id TEXT,
    app_name TEXT,
    tokens INTEGER,
    timestamp DATETIME
);

-- 预聚合统计表
CREATE TABLE usage_stats (
    server_id TEXT,
    app_name TEXT,
    hour TEXT,  -- 格式: 2025-11-23T14
    total_requests INTEGER,
    total_tokens INTEGER,
    PRIMARY KEY (server_id, app_name, hour)
);
```

---

## 总结

所有关键技术决策已明确：
- ✅ 异步代理：httpx.AsyncClient
- ✅ 限流算法：Sliding Window Counter
- ✅ 队列管理：asyncio.Queue + FIFO 驱逐
- ✅ 配置加载：定期轮询数据库（5 秒）
- ✅ 前后端集成：开发分离 + 生产 nginx
- ✅ 数据持久化：aiosqlite + WAL 模式
- ✅ 用量统计：日志 + 定时聚合

**无遗留 NEEDS CLARIFICATION 项，可进入 Phase 1 设计阶段。**
