from .base import FVMBaseError


class PatternFileNotFound(FVMBaseError):
    def __init__(self, path: str):
        super().__init__(f"Arquivo de padrões não encontrado: {path}")


class InvalidPatternFormat(FVMBaseError):
    def __init__(self, detail: str = ""):
        super().__init__(f"Formato de padrão invalido: {detail}")


class NoPatternMatchError(FVMBaseError):
    def __init__(self, pattern: str):
        super().__init__(
            f"Nenhum padrão definido no JSON correspondeu ao texto: {pattern}"
        )
