from .base import APIException


class PatternFileNotFound(APIException):
    def __init__(self, path: str):
        super().__init__(f"Arquivo de padrões não encontrado: {path}")


class InvalidPatternFormat(APIException):
    def __init__(self, detail: str = ""):
        super().__init__(f"Formato de padrão invalido: {detail}")


class NoPatternMatchError(APIException):
    def __init__(self, pattern: str):
        super().__init__(
            f"Nenhum padrão definido no JSON correspondeu ao texto: {pattern}"
        )
