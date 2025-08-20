"""
# File       : api_用户会员管理.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：用户会员管理API - 安全版本
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from svc_user_auth_zxw.db.models import User, Membership, MembershipType, MembershipStatus, Role, App
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.SDK_jwt.jwt import get_current_user
from svc_user_auth_zxw.apis.schemas import (
    用户购买会员请求, 用户会员响应, 用户会员状态更新请求, 通用响应
)
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_user_auth_zxw.tools.error_code import ErrorCode

router = APIRouter(prefix="/memberships", tags=["用户会员管理"])


def _convert_membership_to_response(membership: Membership) -> 用户会员响应:
    """将Membership对象转换为响应格式"""
    return 用户会员响应(
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


async def _check_admin_permission(user: User, db: AsyncSession) -> bool:
    """检查用户是否有管理员权限"""
    # 检查用户是否有admin角色
    has_admin_role = any(
        role.name == "admin" for role in user.roles
    )
    return has_admin_role


async def _require_admin_permission(user: User, db: AsyncSession):
    """要求管理员权限，如果没有则抛出异常"""
    if not await _check_admin_permission(user, db):
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.权限不足,
            detail="需要管理员权限",
            http_status_code=403
        )


# ==================== 内部函数 (不直接暴露API) ====================

async def internal_purchase_membership(
        user_id: int,
        membership_type_id: int,
        payment_verified: bool = False,
        payment_reference: str = None,
        notes: str = None,
        db: AsyncSession = None
) -> 用户会员响应:
    """
    内部会员购买函数 - 只能通过支付验证后调用
    
    Args:
        user_id: 用户ID
        membership_type_id: 会员类型ID
        payment_verified: 支付是否已验证 (必须为True)
        payment_reference: 支付凭证/订单号
        notes: 备注
        db: 数据库会话
    
    Returns:
        用户会员响应对象
        
    Raises:
        HTTPException_AppToolsSZXW: 如果支付未验证或其他错误
    """
    if not payment_verified:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.权限不足,
            detail="支付未验证，无法开通会员",
            http_status_code=403
        )
    
    if not payment_reference:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数错误,
            detail="缺少支付凭证",
            http_status_code=400
        )

    try:
        # 检查用户是否存在
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="用户不存在",
                http_status_code=404
            )

        # 检查会员类型是否存在且启用
        membership_type_result = await db.execute(
            select(MembershipType).where(
                MembershipType.id == membership_type_id,
                MembershipType.is_active == True
            )
        )
        membership_type = membership_type_result.scalar_one_or_none()
        if not membership_type:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员类型不存在或已停用",
                http_status_code=400
            )

        # 检查用户是否已有相同类型的活跃会员
        existing_membership_result = await db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.membership_type_id == membership_type_id,
                Membership.status == MembershipStatus.ACTIVE
            )
        )
        existing_membership = existing_membership_result.scalar_one_or_none()

        now = datetime.utcnow()
        payment_notes = f"支付凭证: {payment_reference}"
        if notes:
            payment_notes += f"\n{notes}"

        if existing_membership and existing_membership.is_valid():
            # 如果已有有效会员，延长到期时间
            existing_membership.end_time = existing_membership.end_time + timedelta(days=membership_type.duration_days)
            existing_membership.updated_at = now
            existing_membership.notes = f"{existing_membership.notes or ''}\n{payment_notes}".strip()

            await db.commit()
            await db.refresh(existing_membership)

            return _convert_membership_to_response(existing_membership)
        else:
            # 创建新的会员记录
            start_time = now
            end_time = start_time + timedelta(days=membership_type.duration_days)

            new_membership = Membership(
                user_id=user_id,
                membership_type_id=membership_type_id,
                start_time=start_time,
                end_time=end_time,
                status=MembershipStatus.ACTIVE,
                notes=payment_notes
            )

            db.add(new_membership)
            await db.commit()
            await db.refresh(new_membership)

            # 加载关联的membership_type
            await db.refresh(new_membership, ["membership_type"])

            return _convert_membership_to_response(new_membership)

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"购买会员失败: {str(e)}",
            http_status_code=500
        )


async def internal_admin_grant_membership(
        admin_user: User,
        target_user_id: int,
        membership_type_id: int,
        duration_days: int = None,
        notes: str = None,
        db: AsyncSession = None
) -> 用户会员响应:
    """
    管理员内部赠送会员函数
    
    Args:
        admin_user: 管理员用户对象
        target_user_id: 目标用户ID
        membership_type_id: 会员类型ID
        duration_days: 自定义天数（可选，默认使用会员类型的天数）
        notes: 备注
        db: 数据库会话
    
    Returns:
        用户会员响应对象
    """
    # 验证管理员权限
    await _require_admin_permission(admin_user, db)
    
    try:
        # 检查目标用户是否存在
        user_result = await db.execute(
            select(User).where(User.id == target_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="目标用户不存在",
                http_status_code=404
            )

        # 检查会员类型
        membership_type_result = await db.execute(
            select(MembershipType).where(MembershipType.id == membership_type_id)
        )
        membership_type = membership_type_result.scalar_one_or_none()
        if not membership_type:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员类型不存在",
                http_status_code=400
            )

        now = datetime.utcnow()
        actual_duration = duration_days or membership_type.duration_days
        admin_notes = f"管理员({admin_user.username})赠送会员"
        if notes:
            admin_notes += f"\n{notes}"

        # 检查是否已有相同类型的活跃会员
        existing_membership_result = await db.execute(
            select(Membership).where(
                Membership.user_id == target_user_id,
                Membership.membership_type_id == membership_type_id,
                Membership.status == MembershipStatus.ACTIVE
            )
        )
        existing_membership = existing_membership_result.scalar_one_or_none()

        if existing_membership and existing_membership.is_valid():
            # 延长现有会员
            existing_membership.end_time = existing_membership.end_time + timedelta(days=actual_duration)
            existing_membership.updated_at = now
            existing_membership.notes = f"{existing_membership.notes or ''}\n{admin_notes}".strip()

            await db.commit()
            await db.refresh(existing_membership)
            return _convert_membership_to_response(existing_membership)
        else:
            # 创建新会员
            start_time = now
            end_time = start_time + timedelta(days=actual_duration)

            new_membership = Membership(
                user_id=target_user_id,
                membership_type_id=membership_type_id,
                start_time=start_time,
                end_time=end_time,
                status=MembershipStatus.ACTIVE,
                notes=admin_notes
            )

            db.add(new_membership)
            await db.commit()
            await db.refresh(new_membership)
            await db.refresh(new_membership, ["membership_type"])

            return _convert_membership_to_response(new_membership)

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"赠送会员失败: {str(e)}",
            http_status_code=500
        )


# ==================== 公开API接口 ====================

@router.get("/my", response_model=通用响应[List[用户会员响应]])
async def 获取我的会员(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """获取当前用户的会员列表"""
    try:
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.user_id == current_user.id)
            .order_by(Membership.created_at.desc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取会员列表失败: {str(e)}",
            http_status_code=500
        )


@router.get("/{membership_id}", response_model=通用响应[用户会员响应])
async def 获取会员详情(
        membership_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """获取会员详情（只能查看自己的或管理员查看所有）"""
    try:
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.id == membership_id)
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员记录不存在",
                http_status_code=404
            )

        # 权限检查：只能查看自己的会员记录，或者管理员可以查看所有
        is_admin = await _check_admin_permission(current_user, db)
        if membership.user_id != current_user.id and not is_admin:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.权限不足,
                detail="无权查看此会员记录",
                http_status_code=403
            )

        return 通用响应(
            data=_convert_membership_to_response(membership),
            message="获取成功"
        )

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取会员详情失败: {str(e)}",
            http_status_code=500
        )


# ==================== 管理员专用API ====================

@router.get("/admin/user/{user_id}", response_model=通用响应[List[用户会员响应]])
async def 管理员获取用户会员(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """管理员获取指定用户的会员列表"""
    try:
        # 验证管理员权限
        await _require_admin_permission(current_user, db)

        # 检查用户是否存在
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="用户不存在",
                http_status_code=404
            )

        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.user_id == user_id)
            .order_by(Membership.created_at.desc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取用户会员列表失败: {str(e)}",
            http_status_code=500
        )


@router.put("/admin/{membership_id}/status", response_model=通用响应[用户会员响应])
async def 管理员更新会员状态(
        membership_id: int,
        request: 用户会员状态更新请求,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """管理员更新会员状态"""
    try:
        # 验证管理员权限
        await _require_admin_permission(current_user, db)

        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.id == membership_id)
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员记录不存在",
                http_status_code=404
            )

        # 更新状态
        membership.status = MembershipStatus(request.status.value)
        membership.updated_at = datetime.utcnow()

        admin_note = f"管理员({current_user.username})更新状态为{request.status.value}"
        if request.notes:
            admin_note += f": {request.notes}"
            
        membership.notes = f"{membership.notes or ''}\n{admin_note}".strip()

        await db.commit()
        await db.refresh(membership)

        return 通用响应(
            data=_convert_membership_to_response(membership),
            message="会员状态更新成功"
        )

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"更新会员状态失败: {str(e)}",
            http_status_code=500
        )


@router.get("/admin/active/all", response_model=通用响应[List[用户会员响应]])
async def 管理员获取所有活跃会员(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """管理员获取所有活跃会员列表"""
    try:
        # 验证管理员权限
        await _require_admin_permission(current_user, db)

        now = datetime.utcnow()
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(
                Membership.status == MembershipStatus.ACTIVE,
                Membership.start_time <= now,
                Membership.end_time >= now
            )
            .offset(skip)
            .limit(limit)
            .order_by(Membership.end_time.asc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取活跃会员列表失败: {str(e)}",
            http_status_code=500
        )


@router.get("/admin/expired/all", response_model=通用响应[List[用户会员响应]])
async def 管理员获取所有过期会员(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """管理员获取所有过期会员列表"""
    try:
        # 验证管理员权限
        await _require_admin_permission(current_user, db)

        now = datetime.utcnow()
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(
                Membership.status == MembershipStatus.ACTIVE,
                Membership.end_time < now
            )
            .offset(skip)
            .limit(limit)
            .order_by(Membership.end_time.desc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取过期会员列表失败: {str(e)}",
            http_status_code=500
        )
