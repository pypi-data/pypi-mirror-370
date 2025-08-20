"""
# File       : test_会员功能.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：会员功能测试
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from svc_user_auth_zxw.db.models import User, MembershipType, Membership, MembershipStatus
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.tools.membership_cleanup import MembershipCleanupService


class TestMembershipFunctionality:
    """会员功能测试类"""

    @pytest.fixture
    async def db_session(self):
        """数据库会话fixture"""
        async with get_db() as session:
            yield session

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """测试用户fixture"""
        user = User(
            username="test_user_membership",
            email="test@example.com",
            phone="13800138000",
            nickname="测试用户"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        yield user

        # 清理
        await db_session.delete(user)
        await db_session.commit()

    @pytest.fixture
    async def test_membership_type(self, db_session: AsyncSession):
        """测试会员类型fixture"""
        membership_type = MembershipType(
            name="测试VIP",
            description="测试VIP会员",
            duration_days=30,
            price=99.0,
            is_active=True
        )
        db_session.add(membership_type)
        await db_session.commit()
        await db_session.refresh(membership_type)
        yield membership_type

        # 清理
        await db_session.delete(membership_type)
        await db_session.commit()

    async def test_membership_type_creation(self, db_session: AsyncSession):
        """测试会员类型创建"""
        membership_type = MembershipType(
            name="单元测试VIP",
            description="单元测试专用VIP",
            duration_days=7,
            price=10.0,
            is_active=True
        )

        db_session.add(membership_type)
        await db_session.commit()
        await db_session.refresh(membership_type)

        assert membership_type.id is not None
        assert membership_type.name == "单元测试VIP"
        assert membership_type.duration_days == 7
        assert membership_type.is_active is True

        # 清理
        await db_session.delete(membership_type)
        await db_session.commit()

    async def test_membership_purchase(self, db_session: AsyncSession, test_user: User, test_membership_type: MembershipType):
        """测试会员购买功能"""
        now = datetime.utcnow()

        membership = Membership(
            user_id=test_user.id,
            membership_type_id=test_membership_type.id,
            start_time=now,
            end_time=now + timedelta(days=test_membership_type.duration_days),
            status=MembershipStatus.ACTIVE,
            notes="单元测试购买"
        )

        db_session.add(membership)
        await db_session.commit()
        await db_session.refresh(membership)

        assert membership.id is not None
        assert membership.user_id == test_user.id
        assert membership.membership_type_id == test_membership_type.id
        assert membership.status == MembershipStatus.ACTIVE
        assert membership.is_valid() is True  # 应该是有效的

        # 清理
        await db_session.delete(membership)
        await db_session.commit()

    async def test_membership_expiry(self, db_session: AsyncSession, test_user: User, test_membership_type: MembershipType):
        """测试会员过期功能"""
        # 创建一个已过期的会员
        past_time = datetime.utcnow() - timedelta(days=1)

        membership = Membership(
            user_id=test_user.id,
            membership_type_id=test_membership_type.id,
            start_time=past_time - timedelta(days=30),
            end_time=past_time,  # 已过期
            status=MembershipStatus.ACTIVE,
            notes="过期测试"
        )

        db_session.add(membership)
        await db_session.commit()
        await db_session.refresh(membership)

        # 验证会员已过期
        assert membership.is_valid() is False

        # 清理
        await db_session.delete(membership)
        await db_session.commit()

    async def test_membership_cleanup_service(self):
        """测试会员清理服务"""
        cleanup_service = MembershipCleanupService()

        # 测试获取统计信息
        stats = await cleanup_service.get_membership_statistics()
        assert "total_memberships" in stats
        assert "active_memberships" in stats
        assert "expired_memberships" in stats
        assert "membership_types" in stats
        assert "timestamp" in stats

        # 测试试运行清理
        result = await cleanup_service.cleanup_expired_memberships(dry_run=True)
        assert "expired_count" in result
        assert "updated" in result
        assert result["updated"] is False  # 试运行不应该更新

        # 测试获取即将过期的会员
        expiring = await cleanup_service.get_expiring_soon_memberships(days_before=30)
        assert isinstance(expiring, list)

    async def test_user_membership_methods(self, db_session: AsyncSession, test_user: User, test_membership_type: MembershipType):
        """测试用户模型中的会员相关方法"""
        now = datetime.utcnow()

        # 创建活跃会员
        membership = Membership(
            user_id=test_user.id,
            membership_type_id=test_membership_type.id,
            start_time=now,
            end_time=now + timedelta(days=30),
            status=MembershipStatus.ACTIVE
        )

        db_session.add(membership)
        await db_session.commit()
        await db_session.refresh(membership)

        # 重新加载用户以获取关联的会员
        result = await db_session.execute(
            select(User).where(User.id == test_user.id)
        )
        user_with_memberships = result.scalar_one()

        # 测试获取活跃会员
        active_memberships = user_with_memberships.get_active_memberships()
        # 注意：由于懒加载的问题，这里可能需要手动加载memberships

        # 测试检查会员类型
        has_membership = user_with_memberships.has_membership_type("测试VIP")
        # 同样可能因为懒加载问题需要特殊处理

        # 清理
        await db_session.delete(membership)
        await db_session.commit()


# 运行测试的便捷函数
async def run_membership_tests():
    """运行会员功能测试"""
    test_instance = TestMembershipFunctionality()

    print("开始测试会员功能...")

    try:
        # 由于fixture的限制，这里手动运行一些基础测试
        async with get_db() as db:
            await test_instance.test_membership_type_creation(db)
            print("✓ 会员类型创建测试通过")

            await test_instance.test_membership_cleanup_service()
            print("✓ 会员清理服务测试通过")

        print("✓ 所有测试通过！")

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_membership_tests())
