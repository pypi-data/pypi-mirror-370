"""
# File       : func_用户id加密.py
# Time       ：2024/12/19
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：用户ID与邀请码的双向加密转换系统
"""

import hashlib
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


class UserIDEncoder:
    """用户ID编码器，支持双向转换并处理大数值溢出"""

    def __init__(self, secret_key: str = None):
        """
        初始化编码器

        Args:
            secret_key: 加密密钥，如果为None则使用默认密钥
        """
        if secret_key is None:
            # 使用项目默认密钥，建议在生产环境中使用环境变量
            secret_key = "svc_user_auth_zxw_default_secret_2024"

        self.secret_key = secret_key

        # 基于密钥生成加密参数
        key_hash = hashlib.sha256(secret_key.encode()).digest()

        # 使用密钥生成XOR掩码（64位）
        self.xor_mask = int.from_bytes(key_hash[:8], byteorder='big')

        # 生成偏移量（避免小ID值太容易被猜测）
        self.offset = int.from_bytes(key_hash[8:16], byteorder='big') % (2 ** 32)

        # 定义邀请码字符集（去掉容易混淆的字符：0, O, I, l, 1）
        self.charset = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        self.base = len(self.charset)

        # 创建字符到数字的映射
        self.char_to_num = {char: i for i, char in enumerate(self.charset)}

        # 最大支持的用户ID值（防止溢出）
        self.max_user_id = 2 ** 53 - 1  # JavaScript安全整数范围

        logger.info(f"用户ID编码器初始化完成，支持最大用户ID：{self.max_user_id}")

    def encode_user_id(self, user_id: int) -> str:
        """
        将用户ID编码为邀请码

        Args:
            user_id: 用户ID

        Returns:
            邀请码字符串

        Raises:
            ValueError: 当用户ID超出支持范围时
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"用户ID必须是正整数，得到：{user_id}")

        if user_id > self.max_user_id:
            raise ValueError(f"用户ID超出支持范围：{user_id} > {self.max_user_id}")

        try:
            # 步骤1：加上偏移量
            offset_id = user_id + self.offset

            # 步骤2：XOR加密
            encrypted_id = offset_id ^ self.xor_mask

            # 步骤3：转换为自定义进制
            if encrypted_id == 0:
                return self.charset[0]

            result = []
            while encrypted_id > 0:
                result.append(self.charset[encrypted_id % self.base])
                encrypted_id //= self.base

            # 反转字符串（高位在前）
            invite_code = ''.join(reversed(result))

            # 步骤4：添加校验位（防止输入错误）
            check_digit = self._calculate_check_digit(invite_code)
            invite_code += check_digit

            logger.debug(f"用户ID {user_id} 编码为邀请码：{invite_code}")
            return invite_code

        except Exception as e:
            logger.error(f"编码用户ID {user_id} 时发生错误：{e}")
            raise ValueError(f"编码失败：{e}")

    def decode_invite_code(self, invite_code: str) -> int:
        """
        将邀请码解码为用户ID

        Args:
            invite_code: 邀请码字符串

        Returns:
            用户ID

        Raises:
            ValueError: 当邀请码格式错误或校验失败时
        """
        if not isinstance(invite_code, str) or len(invite_code) < 2:
            raise ValueError(f"邀请码格式错误：{invite_code}")

        # 转换为大写
        invite_code = invite_code.upper()

        # 检查字符是否都在字符集中
        if not all(c in self.charset for c in invite_code):
            invalid_chars = [c for c in invite_code if c not in self.charset]
            raise ValueError(f"邀请码包含无效字符：{invalid_chars}")

        try:
            # 步骤1：分离校验位
            code_part = invite_code[:-1]
            check_digit = invite_code[-1]

            # 步骤2：验证校验位
            expected_check_digit = self._calculate_check_digit(code_part)
            if check_digit != expected_check_digit:
                raise ValueError("邀请码校验失败")

            # 步骤3：从自定义进制转换回数字
            encrypted_id = 0
            for char in code_part:
                encrypted_id = encrypted_id * self.base + self.char_to_num[char]

            # 步骤4：XOR解密
            offset_id = encrypted_id ^ self.xor_mask

            # 步骤5：减去偏移量
            user_id = offset_id - self.offset

            # 步骤6：验证结果
            if user_id <= 0:
                raise ValueError("解码结果无效")

            if user_id > self.max_user_id:
                raise ValueError(f"解码结果超出支持范围：{user_id}")

            logger.debug(f"邀请码 {invite_code} 解码为用户ID：{user_id}")
            return user_id

        except Exception as e:
            logger.error(f"解码邀请码 {invite_code} 时发生错误：{e}")
            raise ValueError(f"解码失败：{e}")

    def _calculate_check_digit(self, code: str) -> str:
        """
        计算校验位

        Args:
            code: 代码字符串

        Returns:
            校验位字符
        """
        # 使用简单的校验和算法
        checksum = 0
        for i, char in enumerate(code):
            checksum += self.char_to_num[char] * (i + 1)

        return self.charset[checksum % self.base]

    def batch_encode(self, user_ids: list[int]) -> dict[int, str]:
        """
        批量编码用户ID

        Args:
            user_ids: 用户ID列表

        Returns:
            用户ID到邀请码的映射字典
        """
        result = {}
        for user_id in user_ids:
            try:
                result[user_id] = self.encode_user_id(user_id)
            except ValueError as e:
                logger.warning(f"跳过无效用户ID {user_id}：{e}")
                continue

        return result

    def batch_decode(self, invite_codes: list[str]) -> dict[str, int]:
        """
        批量解码邀请码

        Args:
            invite_codes: 邀请码列表

        Returns:
            邀请码到用户ID的映射字典
        """
        result = {}
        for invite_code in invite_codes:
            try:
                result[invite_code] = self.decode_invite_code(invite_code)
            except ValueError as e:
                logger.warning(f"跳过无效邀请码 {invite_code}：{e}")
                continue

        return result

    def validate_invite_code(self, invite_code: str) -> bool:
        """
        验证邀请码是否有效（不进行实际解码）

        Args:
            invite_code: 邀请码字符串

        Returns:
            是否有效
        """
        try:
            self.decode_invite_code(invite_code)
            return True
        except ValueError:
            return False


# 创建全局编码器实例
_default_encoder = None


def get_encoder(secret_key: str = None) -> UserIDEncoder:
    """
    获取编码器实例

    Args:
        secret_key: 可选的密钥，如果为None则使用默认实例

    Returns:
        编码器实例
    """
    global _default_encoder

    if secret_key is None:
        if _default_encoder is None:
            _default_encoder = UserIDEncoder()
        return _default_encoder
    else:
        return UserIDEncoder(secret_key)


def user_id_to_invite_code(user_id: int, secret_key: str = None) -> str:
    """
    将用户ID转换为邀请码

    Args:
        user_id: 用户ID
        secret_key: 可选的密钥

    Returns:
        邀请码字符串
    """
    encoder = get_encoder(secret_key)
    return encoder.encode_user_id(user_id)


def invite_code_to_user_id(invite_code: str, secret_key: str = None) -> int:
    """
    将邀请码转换为用户ID

    Args:
        invite_code: 邀请码字符串
        secret_key: 可选的密钥

    Returns:
        用户ID
    """
    encoder = get_encoder(secret_key)
    return encoder.decode_invite_code(invite_code)


def validate_invite_code(invite_code: str, secret_key: str = None) -> bool:
    """
    验证邀请码是否有效

    Args:
        invite_code: 邀请码字符串
        secret_key: 可选的密钥

    Returns:
        是否有效
    """
    encoder = get_encoder(secret_key)
    return encoder.validate_invite_code(invite_code)


# 示例使用
if __name__ == "__main__":
    # 测试示例
    encoder = UserIDEncoder()

    # 测试各种用户ID
    test_ids = [1, 100, 1000, 10000, 100000, 1000000, 2 ** 32, 2 ** 53 - 1]

    print("=== 用户ID编码测试 ===")
    for user_id in test_ids:
        try:
            invite_code = encoder.encode_user_id(user_id)
            decoded_id = encoder.decode_invite_code(invite_code)
            print(
                f"用户ID: {user_id:>15} -> 邀请码: {invite_code:>10} -> 解码: {decoded_id:>15} {'✓' if decoded_id == user_id else '✗'}")
        except ValueError as e:
            print(f"用户ID: {user_id:>15} -> 错误: {e}")

    print("\n=== 邀请码验证测试 ===")
    valid_code = encoder.encode_user_id(12345)
    print(f"有效邀请码 {valid_code}: {encoder.validate_invite_code(valid_code)}")
    print(f"无效邀请码 'INVALID': {encoder.validate_invite_code('INVALID')}")

    print("\n=== 批量处理测试 ===")
    batch_ids = [1, 2, 3, 100, 999]
    batch_codes = encoder.batch_encode(batch_ids)
    print(f"批量编码: {batch_codes}")

    code_list = list(batch_codes.values())
    batch_decoded = encoder.batch_decode(code_list)
    print(f"批量解码: {batch_decoded}")
