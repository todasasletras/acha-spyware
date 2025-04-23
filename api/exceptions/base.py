class APIException(Exception):
    def __init__(
        self,
        *,
        message: str = "Erro inesperado",
        client_message: str = "Erro interno no servidor",
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
        payload: dict = {},
    ):
        self.message = message
        self.client_message = client_message
        self.status_code = status_code
        self.error_code = error_code
        self.payload = payload

        super().__init__(message)

    def to_dict(self):
        return {"success": False, "error": self.client_message, "code": self.error_code}

    def to_log(self):
        return {
            "status": self.status_code,
            "code": self.error_code,
            "message": self.message,
            "payload": self.payload,
        }
