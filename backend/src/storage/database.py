import aiosqlite
import os
from typing import Optional, List, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager

class Database:
    """数据库操作基类"""
    
    def __init__(self, db_url: str = None):
        if not db_url:
            db_url = os.getenv("DATABASE_URL", "sqlite:///data/gateway.db")
        
        # 处理 sqlite:/// 前缀
        if db_url.startswith("sqlite:///"):
            self.db_path = db_url.replace("sqlite:///", "")
        else:
            self.db_path = db_url
            
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """获取数据库连接上下文管理器"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            yield db

    async def execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """执行 SQL 语句"""
        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        async with self.get_connection() as db:
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """查询多条记录"""
        async with self.get_connection() as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

# 全局实例
_db = None

def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
