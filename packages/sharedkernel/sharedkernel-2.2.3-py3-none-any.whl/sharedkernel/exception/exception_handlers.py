import sentry_sdk
from fastapi import Request,status
import requests
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from sharedkernel.exception import (
                                        BusinessException,
                                        UnAuthorizedException,
                                        CustomException
                                     )
from sharedkernel.objects import Result
from sharedkernel.enum.error_code import ErrorCode


async def http_exception_handler(request: Request, exc: HTTPException):
    sentry_sdk.capture_exception(exc)
    if type(exc)==UnAuthorizedException :
        return await custom_http_exception_handler(
                                                    request,
                                                    CustomException
                                                    (
                                                        status_code= exc.status_code,
                                                        error_code= ErrorCode.UnAuthorized.name,
                                                        detail= ErrorCode.UnAuthorized.value
                                                    )
                                                 )

    return await custom_http_exception_handler(
                                                request,
                                                CustomException
                                                (
                                                    status_code= exc.status_code,
                                                    error_code= requests.status_codes._codes[exc.status_code][0].title(),
                                                    detail= exc.detail
                                                )
                                            )



async def business_http_exception_handler(request: Request, exc: BusinessException):
    sentry_sdk.capture_exception(exc)
    return await custom_http_exception_handler(
                                    request,
                                    CustomException
                                    (
                                        status_code= status.HTTP_400_BAD_REQUEST,
                                        error_code= exc.error_code,
                                        detail= exc.detail
                                    ),
    )

async def custom_http_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
                        status_code=exc.status_code,
                        content= Result(    isSucceed= False,
                                            data= None,
                                            message= exc.detail,
                                            errorCode= exc.error_code
                                        ).__dict__
                     )       


async def exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    return await custom_http_exception_handler(
        request,
        CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.Internal_Server.name,
            detail=ErrorCode.Internal_Server.value
        ),
    )


