"""
# File       : __init__.py.py
# Time       ：2024/9/24 08:23
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from .main import router
from .apis import schemas
# 身份认证体系
from .SDK_jwt.jwt import create_jwt_token, get_current_user, check_jwt_token, oauth2_scheme
from .SDK_jwt.jwt_刷新管理 import create_refresh_token

# 用户角色与权限管理
from .apis.api_用户权限_增加 import add_new_role, delete_role
from .apis.api_用户权限_验证 import require_role, require_roles

# 会员管理
from .apis.api_会员权限验证 import require_membership, require_membership_or_role
from .apis.api_用户会员管理 import internal_purchase_membership
from .apis.api_会员类型管理 import internal_get_membership_types, internal_get_membership_type_by_id, internal_create_membership_type, internal_update_membership_type, internal_delete_membership_type
