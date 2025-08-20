"""
# File       : schemes.py
# Time       ：2024/8/26 下午8:53
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from typing import Union, Optional, List, TypeVar, Generic
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class Payload_Role(BaseModel):
    role_name: str
    app_name: str
    app_id: int


class Payload(BaseModel):
    sub: str = Field(..., title="username", description="必须为用户表中的username字段，且类型必须为str, 否则会报错")
    username: Union[str, None] = None
    nickname: Union[str, None] = None
    roles: list[Payload_Role] = Field(..., title="角色", description="用户角色")


class 请求_获取_登录二维码URL(BaseModel):
    WECHAT_REDIRECT_URI: str


class login_data(BaseModel):
    access_token: str
    refresh_token: str
    user_info: Payload


class 返回_login(BaseModel):
    code: int
    data: login_data


class 请求_更新Token(BaseModel):
    refresh_token: str


class 返回_更新Token(BaseModel):
    access_token: str
    refresh_token: str


class 请求_检查Token_from_body(BaseModel):
    access_token: str


class 请求_验证角色_from_header(BaseModel):
    role_name: str
    app_name: str


class 返回_验证角色_from_header(BaseModel):
    status: bool


class 请求_分配或创建角色(BaseModel):
    user_id: int
    role_name: str
    app_name: str


class 返回_分配或创建角色(BaseModel):
    status: bool
    message: str


class 返回_获取_登录二维码URL(BaseModel):
    qr_code_url: str


class 请求_账号密码_注册(BaseModel):
    username: str
    password: str
    # 增加初始权限
    role_name: str = "l0"
    app_name: str = "auto_write"

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        if len(v) < 4:
            raise ValueError('Password must be at least 4 characters long')
        # if not any(char.isdigit() for char in v):
        #     raise ValueError('Password must contain at least one digit')
        # if not any(char.isalpha() for char in v):
        #     raise ValueError('Password must contain at least one letter')
        return v


class 请求_账号密码_登录(BaseModel):
    username: str
    password: str


class 请求_手机邮箱_注册(BaseModel):
    phone: str
    sms_code: str
    email: str = ""
    email_code: str = ""
    # 增加初始权限
    role_name: str = "l0"
    app_name: str = "app0"
    referer_id: int | None = None


class 请求_手机邮箱_登录(BaseModel):
    username: str|None = None
    phone: str = ""
    sms_code: str = ""
    email: str = ""
    email_code: str = ""
    referer_id: int | str | None = None


class MembershipStatusEnum(str, Enum):
    """会员状态枚举"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


# 会员类型相关schemas
class 会员类型创建请求(BaseModel):
    name: str = Field(..., description="会员类型名称")
    description: Optional[str] = Field(None, description="会员类型描述")
    duration_days: int = Field(..., description="会员有效期天数")
    price: Optional[float] = Field(None, description="价格（元为单位）")
    role_names: Optional[List[str]] = Field([], description="关联的角色名称列表")
    app_name: str = Field(..., description="应用名称")


class 会员类型响应(BaseModel):
    id: int
    name: str
    description: Optional[str]
    duration_days: int
    price: Optional[float]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class 会员类型更新请求(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration_days: Optional[int] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
    role_names: Optional[List[str]] = None
    app_name: Optional[str] = None


# 用户会员相关schemas
class 用户购买会员请求(BaseModel):
    user_id: int = Field(..., description="用户ID")
    membership_type_id: int = Field(..., description="会员类型ID")
    notes: Optional[str] = Field(None, description="备注")


class 用户会员响应(BaseModel):
    id: int
    user_id: int
    membership_type_id: int
    membership_type_name: str
    start_time: datetime
    end_time: datetime
    status: MembershipStatusEnum
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]
    is_valid: bool

    class Config:
        from_attributes = True


class 用户会员状态更新请求(BaseModel):
    status: MembershipStatusEnum = Field(..., description="会员状态")
    notes: Optional[str] = Field(None, description="备注")


class 会员权限验证请求(BaseModel):
    membership_type_name: str = Field(..., description="会员类型名称")
    role_name: str = Field(..., description="角色名称")
    app_name: str = Field(..., description="应用名称")


class 会员权限验证响应(BaseModel):
    has_membership: bool = Field(..., description="是否拥有会员")
    has_permission: bool = Field(..., description="是否拥有权限")
    membership_info: Optional[用户会员响应] = Field(None, description="会员信息")


# 通用响应包装
T = TypeVar('T')


class 通用响应(BaseModel, Generic[T]):
    code: int = 200
    data: T
    message: str = "success"


# 邀请功能相关schemas
class 邀请用户信息(BaseModel):
    """被邀请用户信息"""
    user_id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    created_time: int = Field(..., description="创建时间戳")
    notes: Optional[str] = Field(None, description="备注")

    class Config:
        from_attributes = True


class 邀请人信息(BaseModel):
    """邀请人信息"""
    user_id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")

    class Config:
        from_attributes = True


class 邀请汇总信息响应(BaseModel):
    """邀请汇总信息响应"""
    inviter_info: 邀请人信息 = Field(..., description="邀请人信息")
    invitation_count: int = Field(..., description="邀请总数")
    invitees: List[邀请用户信息] = Field(..., description="被邀请用户列表")
    summary: dict = Field(..., description="汇总统计信息")

    class Config:
        from_attributes = True


class 用户邀请人响应(BaseModel):
    """用户邀请人响应"""
    user_info: dict = Field(..., description="用户信息")
    referrer_info: 邀请人信息 = Field(..., description="邀请人信息")

    class Config:
        from_attributes = True


class 邀请统计信息响应(BaseModel):
    """邀请统计信息响应"""
    user_id: int = Field(..., description="用户ID")
    direct_invitations: int = Field(..., description="直接邀请数量")
    second_level_invitations: int = Field(..., description="二级邀请数量")
    total_network_size: int = Field(..., description="总网络规模")
    statistics_time: str = Field(..., description="统计时间")

    class Config:
        from_attributes = True


class 获取邀请列表请求(BaseModel):
    """获取邀请列表请求"""
    user_id: int = Field(..., description="用户ID")
    limit: Optional[int] = Field(10, description="限制返回数量", ge=1, le=100)
    offset: int = Field(0, description="偏移量", ge=0)


class 绑定邀请人请求(BaseModel):
    """绑定邀请人请求"""
    referer_id: Union[int, str] = Field(..., description="邀请人ID或邀请码")

    class Config:
        json_schema_extra = {
            "example": {
                "referer_id": "ABC123XYZ"  # 可以是数字ID或邀请码字符串
            }
        }


class 绑定邀请人响应(BaseModel):
    """绑定邀请人响应"""
    success: bool = Field(..., description="是否绑定成功")
    referer_info: Optional[邀请人信息] = Field(None, description="邀请人信息")
    message: str = Field(..., description="操作结果消息")

    class Config:
        from_attributes = True
