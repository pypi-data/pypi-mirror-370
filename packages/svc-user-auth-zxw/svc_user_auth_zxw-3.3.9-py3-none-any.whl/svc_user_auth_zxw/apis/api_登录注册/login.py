"""
# File       : login.py
# Time       ：2024/8/22 19:09
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from svc_user_auth_zxw.SDK_jwt.jwt import create_jwt_token
from svc_user_auth_zxw.SDK_jwt.jwt_刷新管理 import create_refresh_token


from svc_user_auth_zxw.db.models import User
from svc_user_auth_zxw.apis.schemas import login_data, Payload

from app_tools_zxw.Errors.api_errors import ErrorCode
from svc_user_auth_zxw.config import 回调配置
from svc_user_auth_zxw.tools.http_exception import HTTPException_VueElementPlusAdmin


async def login_user_async(user: User, db: AsyncSession) -> login_data:
    print("apis/api_登录注册/login.py:login_user_async: user_info=获取中")

    # 回调URL
    if len(回调配置.login_recall) > 0:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    回调配置.login_recall,
                    json={"user_id": user.id, "phone": user.phone}
            ) as response:
                if response.status != 200:
                    raise HTTPException_VueElementPlusAdmin(
                        error_code=ErrorCode.数据创建失败,
                        detail="登录回调请求失败",
                        http_status_code=400
                    )

    # 创建jwt的payload
    payload: Payload = await user.to_payload()

    # 生成jwt token
    access_token = create_jwt_token(payload=payload.model_dump())
    refresh_token = create_refresh_token(user.id, db)
    await db.commit()

    return login_data(
        access_token=access_token,
        refresh_token=refresh_token.token,
        user_info=payload)
