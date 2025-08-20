"""
# File       : 用户验证.py
# Time       ：2024/8/20 下午5:31
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from svc_user_auth_zxw.db.models import User, Role, App
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.apis.schemas import 请求_分配或创建角色, 返回_分配或创建角色

from app_tools_zxw.Errors.api_errors import ErrorCode, HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/roles")


async def delete_role(
        user_id: int,
        role_name: str,
        db: AsyncSession):
    # 1. 查询用户
    user_result = await db.execute(
        select(User).options(selectinload(User.roles)).filter(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.用户未找到,
            detail="用户未找到",
            http_status_code=404
        )

    # 2. 查询角色
    role = next((role for role in user.roles if role.name == role_name), None)
    if not role:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.角色未找到,
            detail="角色未找到",
            http_status_code=404
        )

    # 3. 解除用户与角色关联
    if role in user.roles:
        user.roles.remove(role)
        try:
            await db.commit()
            return {"status": True, "message": "角色删除成功"}
        except Exception as e:
            await db.rollback()
            logger.error(f"角色删除失败: {e}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.角色未找到,
                detail="角色删除失败",
                http_status_code=500
            )
    else:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.角色未找到,
            detail="用户没有该角色",
            http_status_code=400
        )


async def delete_roles(
        user_id: int,
        role_names: list[str],
        db: AsyncSession
):
    # 1. 查询用户
    user_result = await db.execute(
        select(User).options(selectinload(User.roles)).filter(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.用户未找到,
            detail="用户未找到",
            http_status_code=404
        )

    # 2. 查询角色
    wait_for_delete_roles = [role for role in user.roles if role.name in role_names]
    if not wait_for_delete_roles:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.角色未找到,
            detail="角色未找到",
            http_status_code=404
        )

    # 3. 解除用户与角色关联
    for role in wait_for_delete_roles:
        user.roles.remove(role)

    try:
        await db.commit()
        return {"status": True, "message": f"{len(wait_for_delete_roles)}个角色删除成功"}

    except Exception as e:
        await db.rollback()
        logger.error(f"角色删除失败: {e}")
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.角色未找到,
            detail="角色删除失败",
            http_status_code=500
        )


async def add_new_role(
        request: 请求_分配或创建角色,
        db: AsyncSession
):
    """
    分配或创建角色
                如果用户不存在则返回404,
                如果角色不存在则创建角色,
                如果应用不存在则创建应用,
                如果用户和角色都存在则给用户分配角色
    """
    # Eagerly load roles to avoid lazy loading issues
    # 懒加载原理是：当我们访问一个对象的属性时，如果这个属性没有被加载，那么sqlalchemy会自动发起一个sql查询，加载这个属性。
    # 这种加载方式是懒加载，也就是说，当我们访问一个属性时，才会加载这个属性。
    # 但是这种加载方式有一个问题，就是如果我们在一个session中加载了一个对象，然后关闭了这个session，那么这个对象的属性就不能被访问了。
    print("[api - 创建新角色]，request = ", request.model_dump())
    # 1. 查询用户
    result_user = await db.execute(
        select(User).options(selectinload(User.roles)).filter(User.id == request.user_id)
    )
    user = result_user.scalar_one_or_none()

    # 2. 查询app name
    result_app = await db.execute(select(App).filter(App.name == request.app_name))
    app = result_app.scalar_one_or_none()
    # scalar_one_or_none()作用是返回一个结果，如果没有结果则返回None

    # 3. 新增app name , 如果不存在
    if not app:
        app = App(name=request.app_name)
        db.add(app)
        await db.flush()

    # 4. 查询role name
    result_role = await db.execute(select(Role).filter(
        Role.name == request.role_name,
        Role.app == app))
    role = result_role.scalar_one_or_none()

    # 5. 新增role name, 如果不存在.
    if not role:
        role = Role(name=request.role_name, app_id=app.id)
        db.add(role)
        try:
            await db.flush()
        except Exception as e:
            logger.error(f"角色创建失败: {e}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.角色创建失败,
                detail="角色创建失败",
                http_status_code=500
            )

    # 6. 关联user和role
    if user and role:
        user.roles.append(role)
        await db.commit()
        return {"status": True, "message": "角色分配成功"}

    if not user:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.用户未找到,
            detail="用户未找到",
            http_status_code=404
        )

    raise HTTPException_AppToolsSZXW(
        error_code=ErrorCode.角色未找到,
        detail="角色未找到",
        http_status_code=404
    )


class response_分配或创建角色(BaseModel):
    code: int
    data: 返回_分配或创建角色

# @router.post("/assign-role/", response_model=response_分配或创建角色)
# async def __分配或创建角色__(
#         request: 请求_分配或创建角色,
#         db: AsyncSession = Depends(get_db)
# ):
#     return {
#         "code": 200,
#         "data": await add_new_role(request, db)
#     }
