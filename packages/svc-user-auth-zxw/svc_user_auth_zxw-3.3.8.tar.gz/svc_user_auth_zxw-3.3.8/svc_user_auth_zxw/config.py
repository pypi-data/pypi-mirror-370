"""
# File       : config.py
# Time       ：2024/8/20 下午5:25
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pathlib import Path

if Path("configs/config_user_auth.py").exists():
    from configs.config_user_auth import *
else:
    print("没有找到配置文件config_user_auth.py")
    import os
    from datetime import timedelta

    # 测试账号
    TEST_ACCOUNTS = [
        ['13222072002', '6666']
    ]

    # postgresql数据库
    DATABASE_URL = os.environ.get('USER_CENTER_DATABASE_URL')  # 读取docker配置的环境变量
    if not DATABASE_URL:
        DATABASE_URL = "postgresql+asyncpg://...:...@localhost/..."
        os.environ['USER_CENTER_DATABASE_URL'] = DATABASE_URL  # 设置环境变量, 以便在docker、alembic中读取

    # redis数据库 redis://[[username]:[password]]@localhost:6379/0
    REDIS_URL_AUTH = os.environ.get('REDIS_URL_AUTH')
    if not REDIS_URL_AUTH:
        REDIS_URL_AUTH = "redis://[[username]:[password]]@localhost:6379/0"
        os.environ['REDIS_URL_AUTH'] = REDIS_URL_AUTH  # 设置环境变量, 以便在docker、alembic中读取


    class 回调配置:
        login_recall = ""


    # jwt setting
    class JWT:
        SECRET_KEY = "...your_secret_key..."
        ALGORITHM = "HS256"
        expire_time = timedelta(days=7)


    # 微信公众号
    class WeChatPub:
        app_id = "...your_app_id..."
        app_secret = "..."
        scope = "snsapi_login"
        scope_qrcode_login = "snsapi_login"  # 二维码登录必须用snsapi_login
        state = "your_custom_state"  # 用于防止CSRF
        接口配置信息_Token = "..."  # 自己去微信公众号设置


    # 微信小程序
    class WeChatMini:
        app_id = "..."
        app_secret = "..."


    # 阿里云
    class Aliyun:
        ali_access_key_id = "..."
        ali_access_key_secret = "..."
        ali_secretNo_pool_key = "..."


    class AliyunSMS:
        ali_access_key_id = "..."
        ali_access_key_secret = "..."
        ali_secretNo_pool_key = "..."
        sms_template_code = "..."
        sms_签名 = "..."


    # 支付专用
    class WeChatPay:
        MCH_ID = '...'
        SECRET = '...'
        NONCE_STR = '...'
        KEY = '...'
        PAYMENT_NOTIFY_URL = 'https://tongsheng.natapp4.cc/wxpay_recall'
        REFUND_NOTIFY_URL = 'https://tongsheng.natapp4.cc/wxpay_recall'


    # 发送邮件
    class Email:
        sender = '...@163.com'  # 发件人
        server = 'smtp.163.com'  # 所使用的用来发送邮件的SMTP服务器
        username = '...@163.com'  # 发送邮箱的用户名和授权码（不是登录邮箱的密码）
        password = '...'  # 服务器: MVQDSPUQATBDOIFU / 自用电脑: FFHBMPJSXXFEEZIK


    # AES密码密匙
    class AESKey:
        key_web = "..."
        key_local = "..."
