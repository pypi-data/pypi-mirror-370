"""
# File       : invitation_interface.py
# Time       ：2024/12/19
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：邀请功能接口层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, desc
from svc_user_auth_zxw.db.models import User
from datetime import datetime


class InvitationInterface:
    """邀请功能接口类"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_user_invitees(self, user_id: int, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户邀请的所有用户列表

        Args:
            user_id: 邀请人用户ID
            limit: 限制返回数量（可选）
            offset: 偏移量，用于分页

        Returns:
            List[Dict]: 被邀请用户信息列表
        """
        try:
            # 构建查询
            query = (
                select(User)
                .where(User.referer_id == user_id)
                .order_by(desc(User.id))  # 按注册时间倒序
                .offset(offset)
            )

            if limit:
                query = query.limit(limit)

            result = await self.db.execute(query)
            invitees = result.scalars().all()

            # 转换为字典格式
            invitees_list = []
            for invitee in invitees:
                invitees_list.append({
                    "user_id": invitee.id,
                    "username": invitee.username,
                    "nickname": invitee.nickname,
                    "phone": invitee.phone,
                    "email": invitee.email,
                    "created_time": invitee.id,  # 使用ID作为创建时间的参考
                    "notes": invitee.notes
                })

            return invitees_list

        except Exception as e:
            raise Exception(f"获取邀请用户列表失败: {str(e)}")

    async def get_invitation_count(self, user_id: int) -> int:
        """
        获取用户邀请的用户数量

        Args:
            user_id: 邀请人用户ID

        Returns:
            int: 邀请用户数量
        """
        try:
            result = await self.db.execute(
                select(func.count(User.id)).where(User.referer_id == user_id)
            )
            count = result.scalar() or 0
            return count

        except Exception as e:
            raise Exception(f"获取邀请数量失败: {str(e)}")

    async def get_invitation_summary(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户邀请汇总信息

        Args:
            user_id: 邀请人用户ID

        Returns:
            Dict: 包含邀请数量和邀请用户列表的汇总信息
        """
        try:
            # 验证用户是否存在
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError(f"用户ID {user_id} 不存在")

            # 获取邀请数量
            invitation_count = await self.get_invitation_count(user_id)

            # 获取邀请用户列表（默认最多返回100个）
            invitees_list = await self.get_user_invitees(user_id, limit=100)

            return {
                "inviter_info": {
                    "user_id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "phone": user.phone,
                    "email": user.email
                },
                "invitation_count": invitation_count,
                "invitees": invitees_list,
                "summary": {
                    "total_invitations": invitation_count,
                    "displayed_invitations": len(invitees_list),
                    "query_time": datetime.now().isoformat()
                }
            }

        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"获取邀请汇总信息失败: {str(e)}")

    async def get_user_referrer(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户的邀请人信息

        Args:
            user_id: 被邀请用户ID

        Returns:
            Optional[Dict]: 邀请人信息，如果没有邀请人则返回None
        """
        try:
            # 查询用户及其邀请人信息
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.referer))
                .where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"用户ID {user_id} 不存在")

            if not user.referer:
                return None

            return {
                "user_info": {
                    "user_id": user.id,
                    "username": user.username,
                    "nickname": user.nickname
                },
                "referrer_info": {
                    "user_id": user.referer.id,
                    "username": user.referer.username,
                    "nickname": user.referer.nickname,
                    "phone": user.referer.phone,
                    "email": user.referer.email
                }
            }

        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"获取邀请人信息失败: {str(e)}")

    async def get_invitation_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户邀请统计信息

        Args:
            user_id: 用户ID

        Returns:
            Dict: 邀请统计信息
        """
        try:
            # 验证用户是否存在
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError(f"用户ID {user_id} 不存在")

            # 获取直接邀请数量
            direct_invites = await self.get_invitation_count(user_id)

            # 获取二级邀请数量（我邀请的用户再邀请的用户）
            second_level_result = await self.db.execute(
                select(func.count(User.id))
                .where(User.referer_id.in_(
                    select(User.id).where(User.referer_id == user_id)
                ))
            )
            second_level_invites = second_level_result.scalar() or 0

            return {
                "user_id": user_id,
                "direct_invitations": direct_invites,
                "second_level_invitations": second_level_invites,
                "total_network_size": direct_invites + second_level_invites,
                "statistics_time": datetime.now().isoformat()
            }

        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"获取邀请统计信息失败: {str(e)}")


# 便捷函数，用于快速创建接口实例
async def create_invitation_interface(db_session: AsyncSession) -> InvitationInterface:
    """
    创建邀请功能接口实例

    Args:
        db_session: 数据库会话

    Returns:
        InvitationInterface: 邀请功能接口实例
    """
    return InvitationInterface(db_session)
