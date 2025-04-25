from api.models.types.exception import APIErrorCode
from .base import APIException


class CommandExecutionError(APIException):
    """Erro genérico ao executar um comando."""

    pass


class CommandNotFoundError(CommandExecutionError):
    def __init__(self, *, payload={}):
        super().__init__(
            error=APIErrorCode.COMMAND_NOT_FOUND,
            payload=payload,
        )


class CommandPermissionError(CommandExecutionError):
    def __init__(self, *, payload={}):
        super().__init__(
            error=APIErrorCode.COMMAND_PERMISSION_DENIED,
            payload=payload,
        )


class CommandTimeOutError(CommandExecutionError):
    def __init__(
        self, *, message="Tempo limite excedido na execução do comando", payload={}
    ):
        super().__init__(
            error=APIErrorCode.COMMAND_TIMEOUT,
            payload=payload,
        )


class CommandExecutionFailedError(CommandExecutionError):
    def __init__(self, *, payload={}):
        super().__init__(
            error=APIErrorCode.COMMAND_EXECUTION_FAILED,
            payload=payload,
        )


class CommandDependencyMissingError(CommandExecutionError):
    def __init__(self, *, payload={}):
        super().__init__(
            error=APIErrorCode.COMMAND_DEPENDENCY_MISSING,
            payload=payload,
        )


class CommandInputError(CommandExecutionError):
    def __init__(self, *, payload={}):
        super().__init__(
            error=APIErrorCode.INVALID_INPUT,
            payload=payload,
        )


class CommandOutputError(CommandExecutionError):
    def __init__(self, *, payload={}):
        super().__init__(
            error=APIErrorCode.INTERNAL_SERVER_ERROR,
            payload=payload,
        )


class EnvironmentError(CommandExecutionError):
    def __init__(self, *, payload={}):
        super().__init__(
            error=APIErrorCode.INTERNAL_SERVER_ERRORS,
            payload=payload,
        )
