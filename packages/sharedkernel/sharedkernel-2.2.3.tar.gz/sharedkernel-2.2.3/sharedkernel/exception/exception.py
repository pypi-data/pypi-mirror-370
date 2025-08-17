from typing import Any, Dict, Optional
from fastapi import HTTPException, status

from sharedkernel.enum.error_code import ErrorCode


class CustomException(HTTPException):
    def __init__(
        self,
        status_code:int,
        error_code: str,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code= status_code,detail= detail)
        self.headers = headers
        self.error_code = error_code


class BusinessException(HTTPException):
    def __init__(
        self,
        error_code: ErrorCode,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST,detail=error_code.value)
        self.headers = headers
        self.error_code = error_code.name


class UnAuthorizedException(HTTPException):
    def __init__(
            self,
            headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, headers)




