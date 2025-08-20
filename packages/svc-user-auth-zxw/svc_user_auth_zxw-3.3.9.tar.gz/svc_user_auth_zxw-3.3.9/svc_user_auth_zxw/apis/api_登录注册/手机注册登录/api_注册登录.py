import random
import aiohttp
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from svc_user_auth_zxw.db.models import User, Role
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
from app_tools_zxw.Funcs.fastapi_logger import setup_logger
from svc_user_auth_zxw.tools.check_sms_code import SMSCodeChecker
from svc_user_auth_zxw.config import TEST_ACCOUNTS
from svc_user_auth_zxw.tools.func_用户id加密 import invite_code_to_user_id

logger = setup_logger(__name__)

# # 用于存储验证码的字典
# verification_codes = {}


# def store_verification_code(phone: str, code: str):
#     verification_codes[phone] = {
#         "code": code,
#         "expiry": datetime.now() + timedelta(minutes=5)
#     }


# def verify_code(phone: str, code: str) -> bool:
#     if phone not in verification_codes:
#         return False
#     stored_code = verification_codes[phone]
#     if datetime.now() > stored_code["expiry"]:
#         del verification_codes[phone]
#         return False
#     if stored_code["code"] != code:
#         return False
#     del verification_codes[phone]
#     return True


sms = SMS阿里云(AliyunSMS.ali_access_key_id, AliyunSMS.ali_access_key_secret)
router = APIRouter(prefix="/account/phone")
sms_checker = SMSCodeChecker()


async def send_sms_code(phone: str, verification_code: str):
    logger.info(f"send_sms_code:短信模板{AliyunSMS.sms_template_code}, 签名{AliyunSMS.sms_签名}")
    if AliyunSMS.sms_template_code is not None:
        re = await sms.发送_验证码_async(
            phone,
            verification_code,
            短信签名=AliyunSMS.sms_签名)
    else:
        re = await sms.发送_验证码_async(
            phone,
            verification_code,
            AliyunSMS.sms_template_code,
            AliyunSMS.sms_签名)
    return re


@router.post("/send-verification-code/")
async def 发送验证码(phone: str):
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])  # 生成4位随机数字验证码
    result = await send_sms_code(phone, verification_code)
    if result is None:
        await sms_checker.store_verification_code(phone, verification_code)
        return {
            "code": 200,
            "data": {"message": "验证码已发送"}
        }
    else:
        raise HTTPException_VueElementPlusAdmin(
            error_code=ErrorCode.验证码发送失败,
            detail="Failed to send verification code",
            http_status_code=500)


@router.post("/register-phone/", response_model=返回_login)
async def 注册_手机(user_create: 请求_手机邮箱_注册, db: AsyncSession = Depends(get_db)):
    # 检查手机号是否已存在
    result = await db.execute(select(User).filter(User.phone == user_create.phone))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException_VueElementPlusAdmin(error_code=ErrorCode.手机号已注册,
                                                detail="Phone number already registered",
                                                http_status_code=400)
    # 验证验证码
    if not await sms_checker.verify_code(user_create.phone, user_create.sms_code):
        raise HTTPException_VueElementPlusAdmin(error_code=ErrorCode.验证码验证失败,
                                                detail="Invalid verification code",
                                                http_status_code=400)
    # 创建新用户并保存到数据库
    new_user = User(
        username=user_create.phone,
        email=user_create.email if user_create.email else None,
        phone=user_create.phone,
        referer_id=user_create.referer_id if user_create.email else None,
        hashed_password=User.hash_password(user_create.sms_code),
        notes="phone register"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 增加初始权限
    user_info = 请求_分配或创建角色(
        user_id=new_user.id,
        role_name=user_create.role_name,
        app_name=user_create.app_name)
    await add_new_role(user_info, db)

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


@router.post("/login-phone/", response_model=返回_login)
async def 登录_手机(info: 请求_手机邮箱_登录, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.app)
        )
        .filter(User.phone == info.phone)
    )
    user = result.scalar_one_or_none()
    if user is None or not await sms_checker.verify_code(info.phone, info.sms_code):
        raise HTTPException_VueElementPlusAdmin(error_code=ErrorCode.无效的手机号或验证码,
                                                detail="Invalid phone number or SMS code",
                                                http_status_code=400)

    return {
        "code": 200,
        "data": await login_user_async(user, db)
    }


@router.post("/register-or-login-phone/", response_model=返回_login)
async def 注册或登录_手机(info: 请求_手机邮箱_登录, db: AsyncSession = Depends(get_db)):
    # 检查用户是否已存在
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.app)
        )
        .filter(User.phone == info.phone)
    )
    user = result.scalar_one_or_none()

    # 验证验证码
    if not await sms_checker.verify_code(info.phone, info.sms_code):
        # 检查是否是测试账号
        if [info.phone, info.sms_code] not in TEST_ACCOUNTS:
            raise HTTPException_VueElementPlusAdmin(error_code=ErrorCode.验证码验证失败,
                                                    detail="无效的验证码",
                                                    http_status_code=400)
    # 邀请码转user_id
    if isinstance(info.referer_id, str):
        try:
            info.referer_id = invite_code_to_user_id(info.referer_id)
        except ValueError as e:
            info.referer_id = None

    # 用户不存在，执行注册逻辑
    if not user:
        new_user = User(
            username=info.username if info.username else info.phone,
            phone=info.phone,
            referer_id=info.referer_id if info.referer_id else None,
            hashed_password=User.hash_password(info.sms_code),
            notes="phone register and login"
        )
        db.add(new_user)
        await db.commit()

        # 增加初始权限（这里假设使用默认角色，您可能需要调整这部分）
        user_info = 请求_分配或创建角色(
            user_id=new_user.id,
            role_name="l0",
            app_name="app0"
        )
        await add_new_role(user_info, db)
        
        # 重新查询用户以确保所有关联关系都被正确加载
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.app)
            )
            .filter(User.id == new_user.id)
        )
        user = result.scalar_one()

    # 用户存在，执行登录逻辑
    return {
        "code": 200,
        "data": await login_user_async(user, db)
    }
