"""
# File       : http_exception.py
# Time       ：2024/11/21 10:39
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：适配 VUE-ELEMENT-PLUS-ADMIN 的 HTTPException
"""
from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class HTTPException_VueElementPlusAdmin(HTTPException):
    """自定义异常类"""
    def __init__(
        self,
        error_code: int,
        detail: str,
        http_status_code: int = 404
    ):
        self.status_code = http_status_code
        self.detail = {
            "code": error_code,
            "data": detail
        }

# def register_exception(app: FastAPI):
#     """注册 Vue Element Plus Admin 的异常处理器"""
#     @app.exception_handler(HTTPException_VueElementPlusAdmin)
#     async def vue_exception_handler(request: Request, exc: HTTPException_VueElementPlusAdmin):
#         return JSONResponse(
#             status_code=exc.status_code,
#             content=exc.detail
#         )
