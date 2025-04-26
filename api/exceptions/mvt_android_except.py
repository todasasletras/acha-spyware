from api.models.types.exception import APIErrorCode
from .base import APIException


class MVTException(APIException):
    pass


class MVTADBError(MVTException):
    pass


class ADBNotFound(MVTADBError):
    def __init__(self, *, payload=...):
        super().__init__(
            error=APIErrorCode.MVT_ANDROID_CHECKADB_NOT_FOUND, payload=payload
        )
