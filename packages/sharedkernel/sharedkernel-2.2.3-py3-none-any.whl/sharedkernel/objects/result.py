from typing import Generic, TypeVar
from pydantic import BaseModel
from pydantic import BaseModel
from sharedkernel.enum.error_code import ErrorCode

ResultT = TypeVar("ResultT")


class BaseResult(BaseModel):
    isSucceed:bool = True
    message: str = ErrorCode.Success.value
    errorCode: str | None = None

class Result(BaseResult, Generic[ResultT]):
    data: ResultT = None

    def __init__(
        self,
        isSucceed:bool = True,
        data: object | None = None,
        message: str = ErrorCode.Success.value,
        errorCode: str | None = None
        )-> None:
        super().__init__(isSucceed=isSucceed, data=data, message=message, errorCode=errorCode)
