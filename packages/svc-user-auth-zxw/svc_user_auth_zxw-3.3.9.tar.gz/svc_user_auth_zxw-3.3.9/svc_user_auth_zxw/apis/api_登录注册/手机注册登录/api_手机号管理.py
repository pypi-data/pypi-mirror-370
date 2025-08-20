from fastapi import Depends, APIRouter
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from svc_user_auth_zxw.db.models import User
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.apis.api_登录注册.login import login_user_async
from svc_user_auth_zxw.apis.schemas import (返回_login)

from svc_user_auth_zxw.SDK_jwt import (get_current_user)

from svc_user_auth_zxw.tools.http_exception import HTTPException_VueElementPlusAdmin
from app_tools_zxw.Errors.api_errors import ErrorCode
from app_tools_zxw.Funcs.fastapi_logger import setup_logger
from svc_user_auth_zxw.apis.api_登录注册.手机注册登录.api_注册登录 import sms_checker

logger = setup_logger(__name__)
router = APIRouter(prefix="/account/phone")


@router.post("/update-phone/", response_model=返回_login)
async def 更新绑定手机号(
        new_phone: str,
        sms_code: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # 1. 检查新手机号是否已被其他用户使用
    result = await db.execute(select(User).filter(User.phone == new_phone))
    existing_user = result.scalar_one_or_none()
    if existing_user and existing_user.id != user.id:
        raise HTTPException_VueElementPlusAdmin(
            error_code=ErrorCode.手机号已注册,
            detail="Phone number already bound to another user",
            http_status_code=400)

    # 2. 验证 短信验证码
    if user is None or not await sms_checker.verify_code(new_phone, sms_code):
        raise HTTPException_VueElementPlusAdmin(error_code=ErrorCode.无效的手机号或验证码,
                                                detail="Invalid user or SMS code",
                                                http_status_code=400)
    # 3. 更新手机号
    user.phone = new_phone
    await db.commit()

    # 4. 重新登录
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .filter(User.id == user.id)
    )
    user: User | None = result.scalar_one_or_none()
    return {
        "code": 200,
        "data": await login_user_async(user, db)
    }
