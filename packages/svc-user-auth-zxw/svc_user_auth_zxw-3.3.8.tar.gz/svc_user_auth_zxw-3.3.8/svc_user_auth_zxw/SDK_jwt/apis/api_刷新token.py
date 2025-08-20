"""
# File       : api_token刷新.py
# Time       ：2024/8/22 17:47
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app_tools_zxw.SDK_jwt.db_model.model import RefreshToken
from app_tools_zxw.SDK_jwt.jwt import create_jwt_token
from app_tools_zxw.SDK_jwt.jwt_刷新管理 import create_refresh_token

from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.db.models import User

router = APIRouter()


@router.post("/refresh-token/")
async def refreshToken(
        refresh_token: str,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == refresh_token))
    token = result.scalar_one_or_none()

    if token is None or token.is_expired():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = await db.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # Generate a new JWT token
    access_token = create_jwt_token(payload={"sub": user.openid})

    # Optionally, generate a new refresh token
    new_refresh_token = create_refresh_token(user.id, db)
    await db.delete(token)  # Delete the old refresh token
    await db.commit()

    return {
        "code": 200,
        "data": {
            "access_token": access_token,
            "refresh_token": new_refresh_token.token
        }
    }
