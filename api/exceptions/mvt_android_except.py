from api.models.types.exception import APIErrorCode
from .base import APIException


class MVTAndroidException(APIException): ...


class AndroidCheckADBException(MVTAndroidException): ...


class AndroidDownloadAPKException(MVTAndroidException): ...


class ADBNotFoundException(AndroidCheckADBException):
    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.MVT_ANDROID_GENERAL_ERROR, payload=payload)


class CheckABDFailException(AndroidCheckADBException):
    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.DEVICE_CHECKADB_FAILED, payload=payload)


class DeviceNotFoundException(AndroidCheckADBException):
    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.DEVICE_NOT_FOUND, payload=payload)


class USBConnectionFailedException(AndroidCheckADBException):
    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.USB_CONNECTION_FAILED, payload=payload)
