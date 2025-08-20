from setuptools import setup, find_packages

setup(
    name="svc_user_auth_zxw",
    version="3.3.9",
    packages=find_packages(),
    include_package_data=True,  # 确保包含包内的非Python文件
    package_data={
        '': ['**/*.vue', '**/*.ts', '**/*.js', '**/*.html'],  # 包含所有子文件夹中的.vue和.ts文件
    },
    install_requires=[
        'pycryptodome>=3.20.0,<=3.22.0',
        'fastapi>=0.112.0,<0.113',
        'jose>=1.0.0,<1.1.0',
        "aiohttp>=3.12.14",  # 'aiohttp>=3.10.5,<3.11.0'
        'httpx >= 0.28.1',  # >=0.23.3,<=0.27.0
        'sqlalchemy==2.0.32',
        'greenlet==3.0.3',
        'databases==0.9.0',
        "python-jose>=3.4.0",  # 'python-jose==3.3.0'
        'passlib==1.7.4',
        'bcrypt==4.2.0',  # 用于数据库密码加密与校验
        'asyncpg==0.29.0',
        'uvicorn>=0.30.0,<0.31.0',
        "python-multipart>=0.0.19",  # 'python-multipart==0.0.9'
        'app-tools-zxw>=2.2.1',
        'alibabacloud_dysmsapi20170525==3.0.0',
        'redis==5.2.0',
        'apscheduler==3.10.4',
    ],
    author="景募",
    author_email="",
    description="用户权限验证工具包",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunshineinwater/",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
