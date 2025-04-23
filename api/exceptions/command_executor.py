from .base import APIException


class CommandExecutionError(APIException):
    pass


class CommandNotFoundError(CommandExecutionError):
    pass


class CommandPermissionError(CommandExecutionError):
    pass


class CommandTimeOutError(CommandExecutionError):
    pass
