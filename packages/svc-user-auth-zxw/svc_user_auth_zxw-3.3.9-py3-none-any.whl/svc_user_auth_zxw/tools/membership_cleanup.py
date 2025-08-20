"""
# File       : membership_cleanup.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：会员清理工具 - 定期检查和处理过期会员
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from svc_user_auth_zxw.db.models import Membership, MembershipStatus, MembershipType
from svc_user_auth_zxw.db.get_db import get_async_session

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MembershipCleanupService:
    """会员清理服务"""
    
    def __init__(self):
        self.session_factory = get_async_session
    
    async def cleanup_expired_memberships(self, dry_run: bool = False) -> dict:
        """
        清理过期会员
        
        :param dry_run: 是否为试运行（不实际修改数据）
        :return: 清理结果统计
        """
        async with self.session_factory() as db:
            try:
                now = datetime.utcnow()
                
                # 查找所有过期但状态仍为ACTIVE的会员
                result = await db.execute(
                    select(Membership)
                    .options(selectinload(Membership.membership_type))
                    .where(
                        Membership.status == MembershipStatus.ACTIVE,
                        Membership.end_time < now
                    )
                )
                expired_memberships = result.scalars().all()
                
                logger.info(f"发现 {len(expired_memberships)} 个过期会员")
                
                if not dry_run:
                    # 更新过期会员状态
                    for membership in expired_memberships:
                        membership.status = MembershipStatus.EXPIRED
                        membership.updated_at = now
                        logger.info(
                            f"会员过期处理: 用户ID={membership.user_id}, "
                            f"会员类型={membership.membership_type.name}, "
                            f"过期时间={membership.end_time}"
                        )
                    
                    await db.commit()
                    logger.info(f"成功更新 {len(expired_memberships)} 个过期会员状态")
                else:
                    logger.info("试运行模式，不执行实际更新")
                
                return {
                    "expired_count": len(expired_memberships),
                    "updated": not dry_run,
                    "timestamp": now.isoformat()
                }
                
            except Exception as e:
                await db.rollback()
                logger.error(f"清理过期会员失败: {str(e)}")
                raise
    
    async def get_expiring_soon_memberships(self, days_before: int = 7) -> List[dict]:
        """
        获取即将过期的会员（用于发送提醒）
        
        :param days_before: 提前多少天提醒
        :return: 即将过期的会员列表
        """
        async with self.session_factory() as db:
            try:
                now = datetime.utcnow()
                expire_threshold = now + timedelta(days=days_before)
                
                result = await db.execute(
                    select(Membership)
                    .options(
                        selectinload(Membership.membership_type),
                        selectinload(Membership.user)
                    )
                    .where(
                        Membership.status == MembershipStatus.ACTIVE,
                        Membership.end_time > now,
                        Membership.end_time <= expire_threshold
                    )
                    .order_by(Membership.end_time.asc())
                )
                memberships = result.scalars().all()
                
                expiring_list = []
                for membership in memberships:
                    days_remaining = (membership.end_time - now).days
                    expiring_list.append({
                        "membership_id": membership.id,
                        "user_id": membership.user_id,
                        "username": membership.user.username,
                        "membership_type": membership.membership_type.name,
                        "end_time": membership.end_time.isoformat(),
                        "days_remaining": days_remaining
                    })
                
                logger.info(f"发现 {len(expiring_list)} 个即将过期的会员")
                return expiring_list
                
            except Exception as e:
                logger.error(f"获取即将过期会员失败: {str(e)}")
                raise
    
    async def get_membership_statistics(self) -> dict:
        """获取会员统计信息"""
        async with self.session_factory() as db:
            try:
                now = datetime.utcnow()
                
                # 活跃会员数
                active_result = await db.execute(
                    select(Membership).where(
                        Membership.status == MembershipStatus.ACTIVE,
                        Membership.start_time <= now,
                        Membership.end_time >= now
                    )
                )
                active_count = len(active_result.scalars().all())
                
                # 过期会员数
                expired_result = await db.execute(
                    select(Membership).where(
                        Membership.status == MembershipStatus.ACTIVE,
                        Membership.end_time < now
                    )
                )
                expired_count = len(expired_result.scalars().all())
                
                # 总会员数
                total_result = await db.execute(select(Membership))
                total_count = len(total_result.scalars().all())
                
                # 按会员类型统计
                type_stats = {}
                membership_types_result = await db.execute(
                    select(MembershipType).options(selectinload(MembershipType.memberships))
                )
                membership_types = membership_types_result.scalars().all()
                
                for membership_type in membership_types:
                    active_type_count = sum(
                        1 for m in membership_type.memberships
                        if m.status == MembershipStatus.ACTIVE and m.is_valid()
                    )
                    type_stats[membership_type.name] = {
                        "total": len(membership_type.memberships),
                        "active": active_type_count
                    }
                
                return {
                    "total_memberships": total_count,
                    "active_memberships": active_count,
                    "expired_memberships": expired_count,
                    "membership_types": type_stats,
                    "timestamp": now.isoformat()
                }
                
            except Exception as e:
                logger.error(f"获取会员统计失败: {str(e)}")
                raise
    
    async def extend_membership(self, membership_id: int, days: int) -> dict:
        """
        延长会员时间（管理员功能）
        
        :param membership_id: 会员ID
        :param days: 延长天数
        :return: 操作结果
        """
        async with self.session_factory() as db:
            try:
                result = await db.execute(
                    select(Membership)
                    .options(selectinload(Membership.membership_type))
                    .where(Membership.id == membership_id)
                )
                membership = result.scalar_one_or_none()
                
                if not membership:
                    raise ValueError(f"会员记录不存在: {membership_id}")
                
                old_end_time = membership.end_time
                membership.end_time = membership.end_time + timedelta(days=days)
                membership.updated_at = datetime.utcnow()
                
                # 如果会员已过期但要延长，将状态改为活跃
                if membership.status == MembershipStatus.EXPIRED:
                    membership.status = MembershipStatus.ACTIVE
                
                await db.commit()
                
                logger.info(
                    f"会员时间延长: ID={membership_id}, "
                    f"原到期时间={old_end_time}, "
                    f"新到期时间={membership.end_time}, "
                    f"延长天数={days}"
                )
                
                return {
                    "membership_id": membership_id,
                    "old_end_time": old_end_time.isoformat(),
                    "new_end_time": membership.end_time.isoformat(),
                    "extended_days": days,
                    "status": membership.status.value
                }
                
            except Exception as e:
                await db.rollback()
                logger.error(f"延长会员时间失败: {str(e)}")
                raise


# 便捷函数
async def cleanup_expired_memberships(dry_run: bool = False):
    """清理过期会员的便捷函数"""
    service = MembershipCleanupService()
    return await service.cleanup_expired_memberships(dry_run)


async def get_expiring_memberships(days_before: int = 7):
    """获取即将过期会员的便捷函数"""
    service = MembershipCleanupService()
    return await service.get_expiring_soon_memberships(days_before)


async def get_membership_stats():
    """获取会员统计信息的便捷函数"""
    service = MembershipCleanupService()
    return await service.get_membership_statistics()


# 主函数（用于直接运行脚本）
async def main():
    """主函数 - 可以通过命令行直接运行"""
    import argparse
    
    parser = argparse.ArgumentParser(description="会员清理工具")
    parser.add_argument("--cleanup", action="store_true", help="清理过期会员")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--expiring", type=int, default=7, help="查看即将过期的会员（天数）")
    
    args = parser.parse_args()
    
    service = MembershipCleanupService()
    
    try:
        if args.cleanup:
            result = await service.cleanup_expired_memberships(dry_run=args.dry_run)
            print(f"清理结果: {result}")
        
        if args.stats:
            stats = await service.get_membership_statistics()
            print(f"会员统计: {stats}")
        
        if args.expiring > 0:
            expiring = await service.get_expiring_soon_memberships(args.expiring)
            print(f"即将过期的会员 (未来{args.expiring}天): {expiring}")
            
    except Exception as e:
        logger.error(f"执行失败: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 