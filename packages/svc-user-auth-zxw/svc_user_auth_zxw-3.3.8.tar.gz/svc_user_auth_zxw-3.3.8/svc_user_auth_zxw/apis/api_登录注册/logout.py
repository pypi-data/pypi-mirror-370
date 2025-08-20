import random
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from svc_user_auth_zxw.db.models import User
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.apis.api_登录注册.login import login_user_async
from svc_user_auth_zxw.apis.api_用户权限_增加 import add_new_role
from svc_user_auth_zxw.apis.schemas import (返回_login,
                                            请求_分配或创建角色,
                                            请求_手机邮箱_注册,
                                            请求_手机邮箱_登录)

from svc_user_auth_zxw.config import AliyunSMS
from svc_user_auth_zxw.SDK_jwt import (get_current_user)

from svc_user_auth_zxw.tools.http_exception import HTTPException_VueElementPlusAdmin
from app_tools_zxw.SDK_阿里云.SMS_发送短信v2 import SMS阿里云
from app_tools_zxw.Errors.api_errors import ErrorCode
from svc_user_auth_zxw.tools.check_sms_code import SMSCodeChecker


router = APIRouter(prefix="/account")


@router.get("/logout")
async def 退出登录():
    # 删除jwt

    return {
        "code": 200,
        "data": "退出成功"
    }
