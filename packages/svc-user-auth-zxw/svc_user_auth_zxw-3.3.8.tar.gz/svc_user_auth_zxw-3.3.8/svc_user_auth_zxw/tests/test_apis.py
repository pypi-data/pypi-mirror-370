import requests
from app_tools_zxw.Errors.api_errors import ErrorCode

BASE_URL = "http://0.0.0.0:8101"  # 替换为实际的测试服务器URL

phone = "15050560029"
username = "testmmusdsader8iim0"


def test_注册_手机():
    # 测试正常注册
    response = requests.post(f"{BASE_URL}/account/phone/register-phone/", json={
        "phone": phone,
        "sms_code": "123456",
        "role_name": "user_app",
        "app_name": "test_app"
    })

    assert response.status_code == 200
    assert response.json()["data"]["access_token"] is not None

    # 测试重复注册
    response = requests.post(f"{BASE_URL}/account/phone/register-phone/", json={
        "phone": phone,
        "sms_code": "123456",
        "role_name": "user_app",
        "app_name": "test_app"
    })
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == ErrorCode.手机号已注册


def test_登录_手机():
    # 测试正确登录
    response = requests.post(f"{BASE_URL}/account/phone/login-phone/", json={
        "phone": phone,
        "sms_code": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"].keys()

    # 测试错误登录
    response = requests.post(f"{BASE_URL}/account/phone/login-phone/", json={
        "phone": "17512541044",
        "sms_code": "wrong_code"
    })
    assert response.status_code in [400]
    assert response.json()["detail"]["code"] == ErrorCode.无效的手机号或验证码


def test_注册():
    # 测试正常注册
    response = requests.post(f"{BASE_URL}/account/normal/register/", json={
        "username": username,
        "password": "testpassword",
        "role_name": "user_app",
        "app_name": "test_app"
    })
    assert response.status_code == 200
    assert response.json()["data"]["access_token"] is not None

    # 测试重复注册
    response = requests.post(f"{BASE_URL}/account/normal/register/", json={
        "username": username,
        "password": "testpassword",
        "role_name": "user",
        "app_name": "test_app"
    })
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == ErrorCode.用户名已注册


def test_登录():
    # 测试正确登录
    response = requests.post(f"{BASE_URL}/account/normal/login/", json={
        "username": username,
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert response.json()["data"]["access_token"] is not None

    # 测试错误登录
    response = requests.post(f"{BASE_URL}/account/normal/login/", json={
        "username": username,
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == ErrorCode.无效的用户名或密码


def test_获取_登录二维码URL():
    response = requests.post(f"{BASE_URL}/account/wechat/qr-login/get-qrcode", json={
        "WECHAT_REDIRECT_URI": "http://example.com/callback"
    })
    assert response.status_code == 200
    print(response.json())
    assert response.json()["data"]["qr_code_url"] is not None


# 注意：微信一键登录的测试可能需要模拟微信API的响应，这里只是一个简单的示例
def test_一键登录():
    # 这里假设我们有一个有效的微信code
    response = requests.post(f"{BASE_URL}/account/wechat/qr-login/login/", params={
        "code": "valid_wechat_code",
        "app_name": "test_app"
    })
    assert response.status_code == 200
    assert response.json()["data"]["access_token"] is not None

    # 测试无效的code
    response = requests.post(f"{BASE_URL}/account/wechat/qr-login/login/", params={
        "code": "invalid_wechat_code",
        "app_name": "test_app"
    })
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == ErrorCode.微信登录失败
