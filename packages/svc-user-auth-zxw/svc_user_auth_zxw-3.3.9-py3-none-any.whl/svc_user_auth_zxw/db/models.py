"""
# File       : models.py
# Time       ：2024/8/20 下午5:20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint, PrimaryKeyConstraint, DateTime, \
    Text, Enum, Boolean, Float
from datetime import datetime
from passlib.context import CryptContext
from svc_user_auth_zxw.apis.schemas import Payload
import enum
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)
Base = declarative_base()  # 创建一个基类,
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user_role_table = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

# 会员-角色关联表
membership_role_table = Table(
    'membership_role',
    Base.metadata,
    Column('membership_type_id', Integer, ForeignKey('membership_types.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)




class MembershipStatus(enum.Enum):
    """会员状态枚举"""
    ACTIVE = "active"  # 活跃
    EXPIRED = "expired"  # 过期
    SUSPENDED = "suspended"  # 暂停
    CANCELLED = "cancelled"  # 取消


class MembershipType(Base):
    """会员类型表"""
    __tablename__ = "membership_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="会员类型名称，如：VIP、SVIP、普通会员")
    description = Column(Text, comment="会员类型描述")
    duration_days = Column(Integer, nullable=False, comment="会员有效期天数")
    price = Column(Float, comment="价格（元为单位）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 会员类型可以关联多个角色
    roles = relationship(
        "Role",
        secondary=membership_role_table,
        back_populates="membership_types"
    )

    # 反向关系
    memberships = relationship("Membership", back_populates="membership_type")


class Membership(Base):
    """用户会员记录表"""
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    membership_type_id = Column(Integer, ForeignKey('membership_types.id'), nullable=False)

    start_time = Column(DateTime, nullable=False, comment="会员开始时间")
    end_time = Column(DateTime, nullable=False, comment="会员结束时间")
    status = Column(Enum(MembershipStatus), default=MembershipStatus.ACTIVE, comment="会员状态")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    notes = Column(Text, comment="备注")

    # 关联关系
    user = relationship("User", back_populates="memberships")
    membership_type = relationship("MembershipType", back_populates="memberships")

    # 联合唯一索引：同一用户同一时间只能有一个相同类型的活跃会员
    __table_args__ = (
        UniqueConstraint('user_id', 'membership_type_id', 'status', name='uq_user_membership_active'),
    )

    def is_valid(self) -> bool:
        """检查会员是否有效"""
        now = datetime.utcnow()
        return (self.status == MembershipStatus.ACTIVE and
                self.start_time <= now <= self.end_time)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    # 账号 - 必填
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=False, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    openid = Column(String, unique=True, index=True, nullable=True)
    # 密码，可以为空，因为有的用户可能是第三方登录
    hashed_password = Column(String, nullable=True)
    #
    nickname = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    referer_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment="邀请人id")
    referer = relationship("User", remote_side=[id], backref="invitees")

    # secondary作用是指定中间表，back_populates作用是指定反向关系
    # 中间表用于存储多对多关系，反向关系用于在查询时，通过一个表查询另一个表
    # lazy='selectin'表示在查询时，会将关联的表一次性查询出来，而不是按需查询. 可以在fastapi中避免由于session关闭导致的查询异常。
    roles = relationship(
        "Role",
        secondary=user_role_table,
        back_populates="users",
        join_depth=2  # 保留这个设置以确保预加载到 App 层级
    )

    # 会员关系
    memberships = relationship("Membership", back_populates="user")

    def verify_password(self, password: str) -> bool:
        # 密码为空代表是第三方登录
        if password == "":
            return False
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def get_active_memberships(self):
        """获取用户的有效会员"""
        now = datetime.utcnow()
        return [m for m in self.memberships if m.is_valid()]

    def has_membership_type(self, membership_type_name: str) -> bool:
        """检查用户是否有指定类型的有效会员"""
        active_memberships = self.get_active_memberships()
        return any(m.membership_type.name == membership_type_name for m in active_memberships)

    async def to_payload(self) -> Payload:
        # 修改为异步方法
        roles_data = []
        for role in self.roles:
            # 由于使用了 lazy='selectin'，app 关系应该已经被预加载
            # 但为了确保安全，我们先检查 app 是否存在
            app = role.app
            print("[User.to_payload] app = ", app)
            roles_data.append({
                "role_name": role.name,
                "app_id": role.app_id,
                "app_name": app.name if app else None
            })

        return Payload(
            sub=self.username,
            username=self.username,
            nickname=self.nickname,
            roles=roles_data
        )


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    app_id = Column(Integer, ForeignKey('apps.id'))

    # 移除联合主键约束，改为唯一约束
    __table_args__ = (
        UniqueConstraint('name', 'app_id', name='uq_role_name_app_id'),
    )

    app = relationship(
        "App",
        back_populates="roles",
        lazy='selectin'
    )
    users = relationship(
        "User",
        secondary=user_role_table,
        back_populates="roles"
    )

    # 会员类型关系
    membership_types = relationship(
        "MembershipType",
        secondary=membership_role_table,
        back_populates="roles"
    )


class App(Base):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    roles = relationship("Role", back_populates="app")
    UniqueConstraint('name', name='uq_app_name')
