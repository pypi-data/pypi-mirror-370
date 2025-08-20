"""
# File       : api_注册.py
# Time       ：2024/8/22 18:41
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from svc_user_auth_zxw.db.models import User, Role
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.apis.api_登录注册.login import login_user_async
from svc_user_auth_zxw.apis.api_用户权限_增加 import add_new_role
from svc_user_auth_zxw.apis.schemas import (
    返回_login,
    请求_分配或创建角色,
    请求_账号密码_注册,
    请求_账号密码_登录
)
from svc_user_auth_zxw.tools.http_exception import HTTPException_VueElementPlusAdmin

from app_tools_zxw.Errors.api_errors import ErrorCode
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


router = APIRouter(prefix="/account/normal")


@router.post("/register/", response_model=返回_login)
async def 注册(user_create: 请求_账号密码_注册, db: AsyncSession = Depends(get_db)):
    # 检查用户名是否已存在
    result = await db.execute(select(User).filter(User.username == user_create.username))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException_VueElementPlusAdmin(
            error_code=ErrorCode.用户名已注册,
            detail="Username already registered",
            http_status_code=400)
    # 创建新用户并保存到数据库
    new_user = User(
        username=user_create.username,
        # phone=user_create.username,
        # email=user_create.username,
        # openid=user_create.username,
        hashed_password=User.hash_password(user_create.password),
        notes="username register"
    )
    db.add(new_user)
    await db.flush()  # flush 会将更改同步到数据库，但不会提交事务
    # 增加初始权限
    print("apis/api_登录注册/api_注册.py: 注册(): new_user.id = ", new_user.id)
    user_info = 请求_分配或创建角色(
        user_id=new_user.id,
        role_name=user_create.role_name,
        app_name=user_create.app_name
    )
    await add_new_role(user_info, db)
    #
    await db.commit()

    # 重新查询用户以确保所有关联关系都被正确加载
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.app)
        )
        .filter(User.id == new_user.id)
    )
    refreshed_user = result.scalar_one()
    
    return {
        "code": 200,
        "data": await login_user_async(refreshed_user, db)
    }


@router.post("/login/", response_model=返回_login)
async def 登录_(info: 请求_账号密码_登录, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.app)
        )
        .filter(User.username == info.username)
    )
    user = result.scalar_one_or_none()
    logger.info(f"apis/api_登录注册/api_注册.py: 登录(): user = {user}")

    if user is None or not user.verify_password(info.password):
        raise HTTPException_VueElementPlusAdmin(
            error_code=ErrorCode.无效的用户名或密码,
            detail="Invalid username or password",
            http_status_code=400)
    return {
        "code": 200,
        "data": await login_user_async(user, db)
    }


@router.post("/login-form/", response_model=返回_login)
async def 登录_Form数据(login_info: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    #
    username = login_info.username
    password = login_info.password
    #
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.app)
        )
        .filter(User.username == username)
    )
    user = result.scalar_one_or_none()
    print("apis/api_登录注册/api_注册.py: 登录(): user = ", user)

    if user is None or not user.verify_password(password):
        raise HTTPException_VueElementPlusAdmin(
            error_code=ErrorCode.无效的用户名或密码,
            detail="Invalid username or password",
            http_status_code=400)
    return {
        "code": 200,
        "data": await login_user_async(user, db)
    }
