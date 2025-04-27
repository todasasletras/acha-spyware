from api.models.types.exception import APIErrorCode
from api.models.types.schemas import APIResponse


class APIException(Exception):
    def __init__(
        self,
        *,
        error: APIErrorCode = APIErrorCode.SERVER_UNHANDLED_EXCEPTION,
        payload: dict = {},
    ):
        self.message = error.value.internal_message
        self.error = error
        self.client_message = error.value.client_message
        self.status_code = error.value.status_code.name, error.value.status_code.value
        self.payload = payload

        super().__init__(self.message)

    def to_dict(self) -> APIResponse:
        return {
            "success": False,
            "error": self.client_message,
            "code": self.error.value.code,
        }

    def to_log(self):
        return (
            f"status: [{self.status_code[0]}|{self.status_code[1]}], "
            f"code: {self.error.value.code}, "
            f"payload: [{', '.join([f'{key}: {value}' for key, value in self.payload.items()])}] - "
            f"message: {self.error.value.internal_message}, "
        )
