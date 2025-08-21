# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def http_exception_handler(request, exc):
    return JSONResponse(dict(resultCode=exc.status_code, errorString=exc.detail, status="Failed"))


async def validate_exception_handler(request, exc):
    return JSONResponse(dict(resultCode=400, errorString=exc.errors(), status="Failed"))


async def global_exception_handler(request, exc):
    return JSONResponse(dict(resultCode=400, errorString=str(exc), status="Failed"))


EXCEPTION_HANDLERS = {
    HTTPException: http_exception_handler,
    RequestValidationError: validate_exception_handler,
    Exception: global_exception_handler
}
