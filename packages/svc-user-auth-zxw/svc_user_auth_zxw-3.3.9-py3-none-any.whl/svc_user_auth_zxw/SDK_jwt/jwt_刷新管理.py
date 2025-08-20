"""
# File       : jwt_token刷新.py
# Time       ：2024/8/22 17:57
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：在用户登录成功时，生成JWT和刷新令牌，并将刷新令牌存储在数据库中。
"""
import secrets
from datetime import datetime, timedelta
from svc_user_auth_zxw.SDK_jwt.db_model.model import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession


def create_refresh_token(user_id: int, db: AsyncSession, expires_delta: timedelta = timedelta(days=7)):
    token = secrets.token_hex(32)
    expires_at = datetime.utcnow() + expires_delta
    refresh_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(refresh_token)
    return refresh_token
