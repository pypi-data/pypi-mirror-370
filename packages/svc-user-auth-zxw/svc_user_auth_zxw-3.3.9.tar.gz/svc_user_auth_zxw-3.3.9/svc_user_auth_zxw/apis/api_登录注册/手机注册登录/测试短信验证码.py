"""
# File       : 测试短信验证码.py
# Time       ：2024/9/17 09:46
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import asyncio
from app_tools_zxw.SDK_阿里云.SMS_发送短信v2 import SMS阿里云
from svc_user_auth_zxw.config import AliyunSMS

sms = SMS阿里云(AliyunSMS.ali_access_key_id, AliyunSMS.ali_access_key_secret)
if AliyunSMS.sms_template_code is not None:
    re = asyncio.run(sms.发送_验证码_async(
        '17512541044',
        "12345",
        短信签名=AliyunSMS.sms_签名))
else:
    re = asyncio.run(sms.发送_验证码_async(
        '17512541044',
        "12345",
        AliyunSMS.sms_template_code,
        AliyunSMS.sms_签名))

print(re)
