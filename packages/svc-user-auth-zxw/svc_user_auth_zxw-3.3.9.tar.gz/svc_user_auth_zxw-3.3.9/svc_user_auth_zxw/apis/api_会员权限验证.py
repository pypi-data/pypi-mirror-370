"""
# File       : api_会员权限验证.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：会员权限验证API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from svc_user_auth_zxw.db.models import User, MembershipType, App, Membership, MembershipStatus
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.SDK_jwt.jwt import get_current_user
from svc_user_auth_zxw.apis.schemas import (
    会员权限验证请求, 会员权限验证响应, 用户会员响应, 通用响应
)
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Errors.api_errors import ErrorCode
from datetime import datetime

router = APIRouter(prefix="/membership-auth", tags=["会员权限验证"])


def require_membership(membership_type_name: str, app_name: str = None):
    """
    会员权限装饰器 - 检查用户是否拥有指定类型的有效会员

    :param membership_type_name: 会员类型名称
    :param app_name: 应用名称（可选，用于同时检查特定应用权限）
    :return: 权限检查函数
    """
    async def membership_checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        # 检查用户是否有有效会员
        now = datetime.utcnow()
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(
                Membership.user_id == user.id,
                Membership.status == MembershipStatus.ACTIVE,
                Membership.start_time <= now,
                Membership.end_time >= now
            )
            .join(MembershipType)
            .where(MembershipType.name == membership_type_name)
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.权限不足,
                detail=f"需要{membership_type_name}会员权限",
                http_status_code=403
            )

        # 如果指定了应用名称，还需要检查会员类型是否有该应用的权限
        if app_name:
            # 查找应用
            app_result = await db.execute(select(App).where(App.name == app_name))
            app = app_result.scalar_one_or_none()
            if not app:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.应用未找到,
                    detail="应用未找到",
                    http_status_code=404
                )

            # 检查会员类型是否有该应用下的任何角色权限
            membership_type = membership.membership_type
            has_app_permission = any(
                role.app_id == app.id for role in membership_type.roles
            )

            if not has_app_permission:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.权限不足,
                    detail=f"{membership_type_name}会员在应用{app_name}中无权限",
                    http_status_code=403
                )

        return user

    return membership_checker


def require_membership_or_role(membership_type_name: str, role_name: str, app_name: str):
    """
    会员或角色权限装饰器 - 检查用户是否拥有会员权限或角色权限（任一即可）

    :param membership_type_name: 会员类型名称
    :param role_name: 角色名称
    :param app_name: 应用名称
    :return: 权限检查函数
    """
    async def permission_checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        # 首先检查会员权限
        now = datetime.utcnow()
        membership_result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(
                Membership.user_id == user.id,
                Membership.status == MembershipStatus.ACTIVE,
                Membership.start_time <= now,
                Membership.end_time >= now
            )
            .join(MembershipType)
            .where(MembershipType.name == membership_type_name)
        )
        membership = membership_result.scalar_one_or_none()

        if membership:
            return user  # 有有效会员，直接通过

        # 检查角色权限
        app_result = await db.execute(select(App).where(App.name == app_name))
        app = app_result.scalar_one_or_none()
        if not app:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.应用未找到,
                detail="应用未找到",
                http_status_code=404
            )

        has_role = any(
            role.name == role_name and role.app_id == app.id
            for role in user.roles
        )

        if not has_role:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.权限不足,
                detail=f"需要{membership_type_name}会员权限或{role_name}角色权限",
                http_status_code=403
            )

        return user

    return permission_checker


@router.post("/verify", response_model=通用响应[会员权限验证响应])
async def 验证会员权限(
    request: 会员权限验证请求,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """验证用户的会员权限"""
    try:
        # 检查用户是否有指定类型的有效会员
        now = datetime.utcnow()
        membership_result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(
                Membership.user_id == user.id,
                Membership.status == MembershipStatus.ACTIVE,
                Membership.start_time <= now,
                Membership.end_time >= now
            )
            .join(MembershipType)
            .where(MembershipType.name == request.membership_type_name)
        )
        membership = membership_result.scalar_one_or_none()

        has_membership = membership is not None
        has_permission = False
        membership_info = None

        if has_membership:
            membership_info = 用户会员响应(
                id=membership.id,
                user_id=membership.user_id,
                membership_type_id=membership.membership_type_id,
                membership_type_name=membership.membership_type.name,
                start_time=membership.start_time,
                end_time=membership.end_time,
                status=membership.status.value,
                created_at=membership.created_at,
                updated_at=membership.updated_at,
                notes=membership.notes,
                is_valid=membership.is_valid()
            )

            # 检查是否有应用权限
            if request.app_name:
                app_result = await db.execute(
                    select(App).where(App.name == request.app_name)
                )
                app = app_result.scalar_one_or_none()

                if app:
                    membership_type = membership.membership_type
                    # 检查会员类型是否有该应用下的指定角色权限
                    if request.role_name:
                        has_permission = any(
                            role.name == request.role_name and role.app_id == app.id
                            for role in membership_type.roles
                        )
                    else:
                        # 如果没有指定角色，只要有该应用下的任何角色权限即可
                        has_permission = any(
                            role.app_id == app.id for role in membership_type.roles
                        )
                else:
                    has_permission = False
            else:
                has_permission = True  # 如果没有指定应用，只要有会员即可

        return 通用响应(
            data=会员权限验证响应(
                has_membership=has_membership,
                has_permission=has_permission,
                membership_info=membership_info
            ),
            message="验证完成"
        )

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.用户未找到,
            detail=f"会员权限验证失败: {str(e)}",
            http_status_code=500
        )


@router.get("/my-memberships", response_model=通用响应[list])
async def 获取我的有效会员列表(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有有效会员"""
    try:
        now = datetime.utcnow()
        result = await db.execute(
            select(Membership)
            .options(
                selectinload(Membership.membership_type).selectinload(MembershipType.roles)
            )
            .where(
                Membership.user_id == user.id,
                Membership.status == MembershipStatus.ACTIVE,
                Membership.start_time <= now,
                Membership.end_time >= now
            )
            .order_by(Membership.end_time.asc())
        )
        memberships = result.scalars().all()

        membership_data = []
        for membership in memberships:
            # 获取会员类型关联的角色和应用信息
            roles_info = []
            for role in membership.membership_type.roles:
                roles_info.append({
                    "role_name": role.name,
                    "app_id": role.app_id,
                    "app_name": role.app.name if role.app else None
                })

            membership_data.append({
                "id": membership.id,
                "membership_type_name": membership.membership_type.name,
                "start_time": membership.start_time,
                "end_time": membership.end_time,
                "remaining_days": (membership.end_time - now).days,
                "roles": roles_info
            })

        return 通用响应(
            data=membership_data,
            message="获取成功"
        )

    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.用户未找到,
            detail=f"获取有效会员列表失败: {str(e)}",
            http_status_code=500
        )


# 使用示例的路由
@router.get("/vip-data")
async def 获取VIP数据(user: User = Depends(require_membership("VIP"))):
    """VIP会员数据接口示例"""
    return {
        "code": 200,
        "data": "这是VIP会员专享数据",
        "user": user.username
    }


@router.get("/svip-app-data")
async def 获取SVIP应用数据(
        user: User = Depends(require_membership("SVIP", "myapp"))
):
    """SVIP会员特定应用数据接口示例"""
    return {
        "code": 200,
        "data": "这是SVIP会员在myapp应用中的专享数据",
        "user": user.username
    }


@router.get("/premium-or-admin-data")
async def 获取高级权限数据(
        user: User = Depends(require_membership_or_role("Premium", "admin", "myapp"))
):
    """Premium会员或admin角色数据接口示例"""
    return {
        "code": 200,
        "data": "这是Premium会员或admin角色可访问的数据",
        "user": user.username
    }
