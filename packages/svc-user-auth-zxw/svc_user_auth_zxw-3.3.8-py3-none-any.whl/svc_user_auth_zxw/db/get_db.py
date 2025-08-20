"""
# File       : get_db.py
# Time       ：2024/8/20 下午5:22
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from svc_user_auth_zxw.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)
# 创建同步引擎，用于表结构的创建
sync_engine = create_engine(DATABASE_URL)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_async_session():
    """返回异步数据库会话"""
    return AsyncSessionLocal()
