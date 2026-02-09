"""
Database configuration and session management

该模块提供了SQLAlchemy数据库引擎和会话管理功能:
1. 创建同步和异步数据库引擎
2. 配置连接池优化
3. 提供数据库会话依赖注入
4. 支持SQLite和PostgreSQL等多种数据库

设计特点:
- 使用连接池提高并发性能
- 支持同步和异步两种操作模式
- 自动创建数据库表
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from ..core.config import app_config

# Create database URL - 从应用配置获取数据库连接字符串
DATABASE_URL = app_config.database_url

# For async SQLite, we need to use aiosqlite
# 异步SQLite需要特殊处理，使用aiosqlite驱动
if DATABASE_URL.startswith("sqlite:///"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# SQLite-specific configuration for better concurrency
# SQLite数据库特殊配置，解决并发和线程安全问题
sqlite_connect_args = {
    "check_same_thread": False,  # 允许跨线程访问SQLite数据库
    "timeout": 30,  # 等待锁超时时间(秒)
} if "sqlite" in DATABASE_URL else {}

# Create synchronous engine - 同步数据库引擎
# 用于同步的数据库操作，如迁移、初始化等
engine = create_engine(
    DATABASE_URL,
    connect_args=sqlite_connect_args,
    echo=False,  # 禁用SQL日志以减少输出噪音
    pool_pre_ping=True,  # 使用连接前验证连接有效性
    pool_size=100,  # 较大的连接池以支持更好的并发
    max_overflow=200  # 允许溢出连接数
)

# Create asynchronous engine - 异步数据库引擎
# 用于异步API操作，提高Web服务性能
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # 禁用SQL日志以减少输出噪音
    pool_pre_ping=True,
    connect_args={"timeout": 30} if "sqlite" in ASYNC_DATABASE_URL else {}
)

# Create session makers - 创建会话工厂
# 会话用于管理数据库事务和操作
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # 提交后不使对象过期，避免错误
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

def get_db():
    """获取同步数据库会话
    
    FastAPI依赖注入函数，用于获取同步数据库会话
    
    用法:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    
    返回:
        数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """获取异步数据库会话
    
    FastAPI依赖注入函数，用于获取异步数据库会话
    用于异步API端点，提高并发性能
    
    用法:
        @app.get("/")
        async def endpoint(db: AsyncSession = Depends(get_async_db)):
            ...
    
    返回:
        异步数据库会话生成器
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """初始化数据库表
    
    在应用启动时调用，创建所有数据库表
    使用异步引擎执行表创建操作
    """
    # Import here to avoid circular imports
    # 在此处导入以避免循环导入问题
    from .models import Base

    async with async_engine.begin() as conn:
        # Create all tables - 创建所有定义的数据库表
        await conn.run_sync(Base.metadata.create_all)

    # Initialize default admin user
    from ..auth.auth_service import init_default_admin
    db = SessionLocal()
    try:
        init_default_admin(db)
    finally:
        db.close()


async def close_db():
    """Close database connections"""
    await async_engine.dispose()

