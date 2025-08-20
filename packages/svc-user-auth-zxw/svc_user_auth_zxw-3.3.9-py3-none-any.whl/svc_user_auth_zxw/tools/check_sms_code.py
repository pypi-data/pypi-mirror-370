from datetime import datetime, timedelta
from redis import asyncio as aioredis
from typing import Optional
from svc_user_auth_zxw.config import REDIS_URL_AUTH


class SMSCodeChecker:
    def __init__(self, redis_url: str = REDIS_URL_AUTH):
        self.redis = aioredis.from_url(redis_url)
        self.code_expire_minutes = 5

    async def store_verification_code(self, phone: str, code: str) -> None:
        """Store SMS verification code in Redis with expiration"""
        key = f"sms_code:{phone}"
        # Store code with automatic expiration
        await self.redis.set(
            key,
            code,
            ex=self.code_expire_minutes * 60  # Convert minutes to seconds
        )

    async def verify_code(self, phone: str, code: str) -> bool:
        """Verify SMS code and delete it if valid"""
        # if phone == "15050560029":
        #     return True

        key = f"sms_code:{phone}"
        stored_code = await self.redis.get(key)

        if not stored_code:
            return False

        stored_code = stored_code.decode('utf-8')
        if stored_code != code:
            return False

        # Delete the code after successful verification
        await self.redis.delete(key)
        return True

    async def close(self):
        """Close Redis connection"""
        await self.redis.close()
