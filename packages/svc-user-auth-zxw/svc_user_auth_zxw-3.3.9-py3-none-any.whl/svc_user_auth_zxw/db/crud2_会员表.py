"""
# File       : crud2_会员表.py
# Time       ：2024/12/17
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：会员表的CRUD操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from svc_user_auth_zxw.db.models import Membership, MembershipType, User, MembershipStatus
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_user_auth_zxw.tools.error_code import ErrorCode


class PYD_MembershipBase(BaseModel):
    user_id: int
    membership_type_id: int
    start_time: datetime
    end_time: datetime
    status: MembershipStatus = MembershipStatus.ACTIVE
    notes: Optional[str] = None


class PYD_MembershipCreate(PYD_MembershipBase):
    pass


class PYD_MembershipUpdate(BaseModel):
    membership_type_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[MembershipStatus] = None
    notes: Optional[str] = None


class PYD_MembershipResponse(PYD_MembershipBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # 关联信息
    user_name: Optional[str] = None
    membership_type_name: Optional[str] = None

    class Config:
        from_attributes = True


async def create_membership(db: AsyncSession, membership: PYD_MembershipCreate) -> PYD_MembershipResponse:
    """创建会员记录"""
    try:
        # 检查用户是否存在
        user_query = select(User).where(User.id == membership.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(ErrorCode.用户未找到, f"用户ID {membership.user_id} 不存在")

        # 检查会员类型是否存在
        membership_type_query = select(MembershipType).where(MembershipType.id == membership.membership_type_id)
        membership_type_result = await db.execute(membership_type_query)
        membership_type = membership_type_result.scalar_one_or_none()
        if not membership_type:
            raise HTTPException_AppToolsSZXW(ErrorCode.会员类型不存在, f"会员类型ID {membership.membership_type_id} 不存在")

        # 检查是否已存在相同类型的活跃会员
        existing_query = select(Membership).where(
            and_(
                Membership.user_id == membership.user_id,
                Membership.membership_type_id == membership.membership_type_id,
                Membership.status == MembershipStatus.ACTIVE
            )
        )
        existing_result = await db.execute(existing_query)
        existing_membership = existing_result.scalar_one_or_none()
        if existing_membership:
            raise HTTPException_AppToolsSZXW(ErrorCode.会员已存在, f"用户已存在相同类型的活跃会员")

        new_membership = Membership(**membership.model_dump())
        db.add(new_membership)
        await db.commit()
        await db.refresh(new_membership)

        # 手动创建 PYD_MembershipResponse 实例
        return PYD_MembershipResponse(
            id=new_membership.id,
            user_id=new_membership.user_id,
            membership_type_id=new_membership.membership_type_id,
            start_time=new_membership.start_time,
            end_time=new_membership.end_time,
            status=new_membership.status,
            notes=new_membership.notes,
            created_at=new_membership.created_at,
            updated_at=new_membership.updated_at,
            user_name=user.username,
            membership_type_name=membership_type.name
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(ErrorCode.新增数据失败, f"创建会员记录失败: {str(e)}")


async def get_membership(
        db: AsyncSession,
        membership_id: Optional[int] = None,
        user_id: Optional[int] = None,
        include_details: bool = False) -> Optional[PYD_MembershipResponse]:
    """获取会员记录
    
    Args:
        db: 数据库会话
        membership_id: 会员记录ID（可选）
        user_id: 用户ID（可选，如果提供则返回该用户最新的会员记录）
        include_details: 是否包含关联信息
    
    Returns:
        会员记录或None
    
    Raises:
        HTTPException_AppToolsSZXW: 当参数不合法时抛出异常
    """
    if not membership_id and not user_id:
        raise HTTPException_AppToolsSZXW(ErrorCode.参数错误, "membership_id 和 user_id 至少需要提供一个参数")
    
    if membership_id and user_id:
        raise HTTPException_AppToolsSZXW(ErrorCode.参数错误, "membership_id 和 user_id 不能同时提供")

    query = select(Membership)
    
    if membership_id:
        query = query.where(Membership.id == membership_id)
    else:
        # 通过user_id查询，返回最新的会员记录
        query = query.where(Membership.user_id == user_id).order_by(Membership.created_at.desc())

    if include_details:
        query = query.options(
            joinedload(Membership.user),
            joinedload(Membership.membership_type)
        )

    result = await db.execute(query)
    membership = result.unique().scalar_one_or_none()

    if not membership:
        return None

    membership_dict = {
        "id": membership.id,
        "user_id": membership.user_id,
        "membership_type_id": membership.membership_type_id,
        "start_time": membership.start_time,
        "end_time": membership.end_time,
        "status": membership.status,
        "notes": membership.notes,
        "created_at": membership.created_at,
        "updated_at": membership.updated_at,
    }

    if include_details:
        membership_dict["user_name"] = membership.user.username if membership.user else None
        membership_dict["membership_type_name"] = membership.membership_type.name if membership.membership_type else None

    return PYD_MembershipResponse(**membership_dict)


async def update_membership(
        db: AsyncSession,
        membership_id: int,
        membership_update: PYD_MembershipUpdate) -> Optional[PYD_MembershipResponse]:
    """更新会员记录"""
    try:
        query = select(Membership).where(Membership.id == membership_id)
        result = await db.execute(query)
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException_AppToolsSZXW(ErrorCode.会员记录不存在, f"未找到要更新的会员记录: {membership_id}")

        # 如果要更新会员类型，需要检查新类型是否存在
        if membership_update.membership_type_id:
            membership_type_query = select(MembershipType).where(MembershipType.id == membership_update.membership_type_id)
            membership_type_result = await db.execute(membership_type_query)
            membership_type = membership_type_result.scalar_one_or_none()
            if not membership_type:
                raise HTTPException_AppToolsSZXW(ErrorCode.会员类型不存在, f"会员类型ID {membership_update.membership_type_id} 不存在")

        # 更新字段
        for field, value in membership_update.model_dump(exclude_unset=True).items():
            setattr(membership, field, value)

        membership.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(membership)

        # 获取关联信息
        user_query = select(User).where(User.id == membership.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        membership_type_query = select(MembershipType).where(MembershipType.id == membership.membership_type_id)
        membership_type_result = await db.execute(membership_type_query)
        membership_type = membership_type_result.scalar_one_or_none()

        return PYD_MembershipResponse(
            id=membership.id,
            user_id=membership.user_id,
            membership_type_id=membership.membership_type_id,
            start_time=membership.start_time,
            end_time=membership.end_time,
            status=membership.status,
            notes=membership.notes,
            created_at=membership.created_at,
            updated_at=membership.updated_at,
            user_name=user.username if user else None,
            membership_type_name=membership_type.name if membership_type else None
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(ErrorCode.更新数据失败, f"更新会员记录失败: {str(e)}")


async def delete_membership(db: AsyncSession, membership_id: int) -> bool:
    """删除会员记录"""
    try:
        query = delete(Membership).where(Membership.id == membership_id)
        result = await db.execute(query)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(ErrorCode.会员记录不存在, f"未找到要删除的会员记录: {membership_id}")

        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(ErrorCode.删除数据失败, f"删除会员记录失败: {str(e)}")


async def list_memberships(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        membership_type_id: Optional[int] = None,
        status: Optional[MembershipStatus] = None,
        include_details: bool = False) -> List[PYD_MembershipResponse]:
    """获取会员记录列表"""
    query = select(Membership)

    if include_details:
        query = query.options(
            joinedload(Membership.user),
            joinedload(Membership.membership_type)
        )

    # 添加筛选条件
    if user_id:
        query = query.where(Membership.user_id == user_id)
    if membership_type_id:
        query = query.where(Membership.membership_type_id == membership_type_id)
    if status:
        query = query.where(Membership.status == status)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    memberships = result.unique().scalars().all()

    membership_responses = []
    for membership in memberships:
        membership_dict = {
            "id": membership.id,
            "user_id": membership.user_id,
            "membership_type_id": membership.membership_type_id,
            "start_time": membership.start_time,
            "end_time": membership.end_time,
            "status": membership.status,
            "notes": membership.notes,
            "created_at": membership.created_at,
            "updated_at": membership.updated_at,
        }

        if include_details:
            membership_dict["user_name"] = membership.user.username if membership.user else None
            membership_dict["membership_type_name"] = membership.membership_type.name if membership.membership_type else None

        membership_responses.append(PYD_MembershipResponse(**membership_dict))

    return membership_responses


async def get_user_active_memberships(db: AsyncSession, user_id: int) -> List[PYD_MembershipResponse]:
    """获取用户的有效会员记录"""
    now = datetime.utcnow()
    query = select(Membership).options(
        joinedload(Membership.user),
        joinedload(Membership.membership_type)
    ).where(
        and_(
            Membership.user_id == user_id,
            Membership.status == MembershipStatus.ACTIVE,
            Membership.start_time <= now,
            Membership.end_time >= now
        )
    )

    result = await db.execute(query)
    memberships = result.unique().scalars().all()

    membership_responses = []
    for membership in memberships:
        membership_responses.append(PYD_MembershipResponse(
            id=membership.id,
            user_id=membership.user_id,
            membership_type_id=membership.membership_type_id,
            start_time=membership.start_time,
            end_time=membership.end_time,
            status=membership.status,
            notes=membership.notes,
            created_at=membership.created_at,
            updated_at=membership.updated_at,
            user_name=membership.user.username if membership.user else None,
            membership_type_name=membership.membership_type.name if membership.membership_type else None
        ))

    return membership_responses


async def expire_membership(db: AsyncSession, membership_id: int) -> bool:
    """手动过期会员记录"""
    try:
        query = select(Membership).where(Membership.id == membership_id)
        result = await db.execute(query)
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException_AppToolsSZXW(ErrorCode.会员记录不存在, f"未找到会员记录: {membership_id}")

        membership.status = MembershipStatus.EXPIRED
        membership.updated_at = datetime.utcnow()
        await db.commit()

        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(ErrorCode.更新数据失败, f"过期会员记录失败: {str(e)}")
