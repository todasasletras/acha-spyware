import subprocess
from typing import List

from api.interfaces.command_executor_interface import CommandExecutorInterface
from api.models.types.schemas import APIResponse, LogMessageEntry
from api.exceptions import (
    CommandExecutionError,
    CommandNotFoundError,
    CommandPermissionError,
    CommandTimeOutError,
    CommandExecutionFailedError,
    CommandDependencyMissingError,
    CommandOutputError,
)
from core.logger import setup_logger
from .log_parser import LogParser

logger = setup_logger()
log = LogParser()


class CommandExecutor(CommandExecutorInterface):
    def run_command(self, command) -> List[LogMessageEntry]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                stderr_lower = result.stderr.lower()

                if "not found" in stderr_lower:
                    raise CommandNotFoundError(payload={"stderr": result.stdout})

                elif "permission denied" in stderr_lower:
                    raise CommandPermissionError(payload={"stderr": result.stdout})

                elif (
                    "command not found" in stderr_lower
                    or "no such file" in stderr_lower
                ):
                    raise CommandDependencyMissingError(
                        payload={"stderr": result.stdout}
                    )

            if not result.stdout.strip():
                raise CommandOutputError(payload={"stdout": result.stdout})

            return log.parse(result.stdout)

        except (
            CommandNotFoundError,
            CommandPermissionError,
            CommandDependencyMissingError,
            CommandExecutionFailedError,
            CommandOutputError,
            CommandTimeOutError,
            CommandExecutionError,
        ) as e:
            raise self._handle_exception(type(e), payload=e.payload)
        except subprocess.TimeoutExpired as timeout:
            raise self._handle_exception(
                CommandTimeOutError, payload={"command": command, "error": str(timeout)}
            )

        except OSError as e:
            raise self._handle_exception(
                CommandNotFoundError, payload={"command": command, "error": str(e)}
            )
        except Exception as e:
            print(e)
            raise self._handle_exception(
                CommandExecutionFailedError,
                payload={"command": command, "error": str(e)},
            )

    def _handle_exception(self, exc_class, payload=None) -> APIResponse:
        api_except = exc_class(payload=payload or {})
        logger.error(api_except.to_log())
        return api_except


if __name__ == "__main__":
    print(CommandExecutor().run_command(["mvt-android"]))
