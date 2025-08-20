"""
# File       : login.py
# Time       ：2024/8/22 19:09
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pydantic import BaseModel
from app_tools_zxw.SDK_jwt.jwt import create_jwt_token
from app_tools_zxw.SDK_jwt.jwt_刷新管理 import create_refresh_token
from sqlalchemy.ext.asyncio import AsyncSession
from svc_user_auth_zxw.db.models import User


class LoginResponse(BaseModel):
    jwt_token: str
    refresh_token: str


async def login_user(user: User, db: AsyncSession) -> LoginResponse:
    user_info = {"user_id": user.id, "roles": [role.name for role in user.roles]}
    access_token = create_jwt_token(data=user_info)
    refresh_token = create_refresh_token(user.id, db)
    await db.commit()
    return LoginResponse(jwt_token=access_token, refresh_token=refresh_token.token)
