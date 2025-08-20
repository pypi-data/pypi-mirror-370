"""
# File       : api_刷新JWT.py
# Time       ：2024/8/22 18:00
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.db.models import User
from svc_user_auth_zxw.SDK_jwt import (
    create_jwt_token,
    create_refresh_token,
    RefreshToken,
    get_current_user)
from svc_user_auth_zxw.SDK_jwt.jwt import check_jwt_token, oauth2_scheme
from svc_user_auth_zxw.apis.schemas import (
    请求_更新Token,
    返回_更新Token,
    请求_检查Token_from_body,
    Payload)

router = APIRouter(prefix="/token")


class response_获取当前用户(BaseModel):
    code: int
    data: Payload


@router.post("/get-current-user/", response_model=response_获取当前用户)
async def 获取当前用户(user: User = Depends(get_current_user)) -> Payload:
    return {
        "code": 200,
        "data": await user.to_payload()
    }


class response_更新Token(BaseModel):
    code: int
    data: 返回_更新Token


@router.post("/refresh-token/", response_model=response_更新Token)
async def 更新token(refresh_token: 请求_更新Token, db: AsyncSession = Depends(get_db)):
    refresh_token = refresh_token.refresh_token
    # Check if the refresh token is valid
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == refresh_token))
    token = result.scalar_one_or_none()

    if token is None or token.is_expired():
        raise HTTPException(
            status_code=401,
            detail={
                "code": 401,
                "data": "Invalid or expired refresh token"
            }
        )

    user = await db.get(User, token.user_id)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": 401,
                "data": "User not found"
            }
        )

    # 创建payload
    payload: Payload = await user.to_payload()

    # Generate a new JWT token
    access_token = create_jwt_token(payload=payload.model_dump())

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


async def validate_token(access_token: str) -> Payload:
    payload = check_jwt_token(access_token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": 401,
                "data": "Invalid token"
            }
        )
    return payload


@router.post("/check-token-from-body/", response_description="返回payload")
async def 检查token_from_body(access_token: 请求_检查Token_from_body):
    access_token = access_token.access_token
    return {
        "code": 200,
        "data": await validate_token(access_token)
    }


@router.post("/check-token-from-header/", response_description="返回payload")
async def 检查token_from_header(access_token: str = Depends(oauth2_scheme)):
    return {
        "code": 200,
        "data": await validate_token(access_token)
    }
