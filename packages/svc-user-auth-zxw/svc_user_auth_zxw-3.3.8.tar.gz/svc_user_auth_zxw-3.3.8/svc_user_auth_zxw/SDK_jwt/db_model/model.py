"""
# File       : model.py
# Time       ：2024/8/22 18:06
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：此处与项目存在耦合，复用时需要解耦。
"""
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime
from datetime import datetime
# 耦合1：此处导入根据具体项目的路径而定，User为自定义的用户模型
from svc_user_auth_zxw.db.models import Base, User


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # 耦合2："users.id"
    user = relationship("User", back_populates="refresh_tokens")  # 耦合3："User"
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at


# # 耦合4：back_populates="user"
# 在User中添加refresh_tokens属性，用于关联RefreshToken表。cascade="all, delete-orphan"表示级联删除
# cascade="all, delete-orphan": 级联选项意味着，当删除 User 时，会自动删除所有与之关联的 RefreshToken（孤儿对象），以保持数据库的一致性。
User.refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
