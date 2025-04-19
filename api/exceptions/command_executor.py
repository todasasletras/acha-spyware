from .base import FVMBaseError


class CommandExecutionError(FVMBaseError):
    pass


class CommandNotFoundError(CommandExecutionError):
    pass


class CommandPermissionError(CommandExecutionError):
    pass


class CommandTimeOutError(CommandExecutionError):
    pass
