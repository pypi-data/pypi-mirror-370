from enum import Enum


class ErrorCode(str, Enum):
    Item_NotFound = "یافت نشد"
    Internal_Server = "خطایی در سیستم رخ داده است"
    UnAuthorized = "توکن دسترسی معتبر نمی باشد"
    Success = "با موفقیت انجام شد"
    Intents_Count_Should_Equal_One = "فقط یک اینتنت میتوانید وارد نمایید"
    Unsupported_Date_Type = "تاریخ داده شده پیشتیبانی نمیشود."
