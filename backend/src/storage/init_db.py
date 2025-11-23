import asyncio
import logging
from src.storage.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """初始化数据库表结构"""
    db = get_db()
    logger.info(f"Initializing database at {db.db_path}")

    # 1. ServerConfig 表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS server_configs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            api_key TEXT NOT NULL,
            models TEXT NOT NULL, -- JSON Array
            rpm_limit INTEGER NOT NULL,
            tpm_limit INTEGER NOT NULL,
            queue_max_size INTEGER NOT NULL DEFAULT 100,
            queue_timeout_seconds INTEGER NOT NULL DEFAULT 30,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """)
    logger.info("Created table: server_configs")

    # 2. RequestLog 表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS request_logs (
            id TEXT PRIMARY KEY,
            server_id TEXT NOT NULL,
            app_name TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL DEFAULT 0,
            completion_tokens INTEGER NOT NULL DEFAULT 0,
            total_tokens INTEGER NOT NULL DEFAULT 0,
            status_code INTEGER NOT NULL,
            latency_ms INTEGER NOT NULL,
            is_queued BOOLEAN NOT NULL DEFAULT 0,
            queue_wait_ms INTEGER,
            error_message TEXT,
            timestamp TIMESTAMP NOT NULL,
            FOREIGN KEY (server_id) REFERENCES server_configs (id)
        )
    """)
    # 创建索引
    await db.execute("CREATE INDEX IF NOT EXISTS idx_request_logs_stats ON request_logs (server_id, app_name, timestamp)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_request_logs_timestamp ON request_logs (timestamp)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_request_logs_server_time ON request_logs (server_id, timestamp)")
    logger.info("Created table: request_logs")

    # 3. UsageStats 表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS usage_stats (
            server_id TEXT NOT NULL,
            app_name TEXT NOT NULL,
            time_bucket TEXT NOT NULL,
            bucket_type TEXT NOT NULL,
            total_requests INTEGER NOT NULL DEFAULT 0,
            successful_requests INTEGER NOT NULL DEFAULT 0,
            failed_requests INTEGER NOT NULL DEFAULT 0,
            total_tokens INTEGER NOT NULL DEFAULT 0,
            avg_latency_ms REAL NOT NULL DEFAULT 0,
            queued_requests INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP NOT NULL,
            PRIMARY KEY (server_id, app_name, time_bucket, bucket_type),
            FOREIGN KEY (server_id) REFERENCES server_configs (id)
        )
    """)
    logger.info("Created table: usage_stats")

    logger.info("Database initialization completed.")

if __name__ == "__main__":
    asyncio.run(init_db())
