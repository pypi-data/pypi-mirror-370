"""
# File       : 微信一键登录.py
# Time       ：2024/8/20 下午5:24
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from svc_user_auth_zxw.db.models import User, Role
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.config import WeChatPub
from svc_user_auth_zxw.apis.api_登录注册.login import login_user_async
from svc_user_auth_zxw.apis.api_用户权限_增加 import add_new_role
from svc_user_auth_zxw.apis.schemas import (
    返回_login,
    请求_分配或创建角色,
    请求_获取_登录二维码URL,
    返回_获取_登录二维码URL,
)

from app_tools_zxw.SDK_微信.SDK_微信公众号或网站应用.获取_openid和access_token import get_access_token_and_openid_async
from app_tools_zxw.SDK_微信.SDK_微信公众号或网站应用.获取_登录二维码URL import get_qrcode_url
from app_tools_zxw.Errors.api_errors import ErrorCode
from svc_user_auth_zxw.tools.http_exception import HTTPException_VueElementPlusAdmin

router = APIRouter(prefix="/account/wechat/qr-login", tags=["微信一键登录"])


class response_获取_登录二维码URL(BaseModel):
    code: int
    data: 返回_获取_登录二维码URL


@router.post("/get-qrcode", response_model=response_获取_登录二维码URL)
async def 获取_登录二维码URL(url: 请求_获取_登录二维码URL):
    """
    :param WECHAT_REDIRECT_URI: 与网页授权获取用户信息里的回调域名一致
    :return:
    """
    try:
        qrcode_url = get_qrcode_url(url.WECHAT_REDIRECT_URI, WeChatPub.scope_qrcode_login)
        return {
            "code": 200,
            "data": 返回_获取_登录二维码URL(qr_code_url=qrcode_url)
        }

    except Exception as e:
        raise HTTPException_VueElementPlusAdmin(
            error_code=ErrorCode.生成二维码失败,
            detail="Failed to generate WeChat QR code URL",
            http_status_code=500)


@router.post("/login/", response_model=返回_login)
async def 一键登录(code: str, app_name: str, db: AsyncSession = Depends(get_db)):
    """
    逻辑：通过code获取openid，然后判断是否存在用户，不存在则创建用户
    :param code: 微信登录code
    :param app_name: app名称
    :param db:
    :return:
    """
    access_key, openid = await get_access_token_and_openid_async(
        code,
        WeChatPub.app_id,
        WeChatPub.app_secret)

    if openid:
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.app)
            )
            .filter(User.openid == openid)
        )
        user = result.scalar_one_or_none()
        if not user:
            user = User(openid=openid,
                        username=openid,
                        phone=openid,
                        email=openid,
                        nickname="WeChatPub User")
            db.add(user)
            await db.commit()
            # 增加初始权限
            user_info = 请求_分配或创建角色(user_id=user.id,
                                            role_name="l0",
                                            app_name=app_name)
            await add_new_role(user_info, db)
            
            # 重新查询用户以确保所有关联关系都被正确加载
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.roles).selectinload(Role.app)
                )
                .filter(User.id == user.id)
            )
            user = result.scalar_one()
        #
        return {
            "code": 200,
            "data": await login_user_async(user, db)
        }

    raise HTTPException_VueElementPlusAdmin(
        error_code=ErrorCode.微信登录失败,
        detail="Login failed",
        http_status_code=400)
