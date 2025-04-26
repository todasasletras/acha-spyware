import subprocess
from typing import List

from api.interfaces.command_executor_interface import CommandExecutorInterface
from api.models.types.schemas import LogMessageEntry
from api.exceptions.command_executor import (
    CommandNotFoundError,
    CommandPermissionError,
    CommandTimeOutError,
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
                    notfound_error = CommandNotFoundError(
                        payload={"stderr": result.stdout}
                    )
                    logger.error(notfound_error.to_log())
                    raise notfound_error

                elif "permission denied" in stderr_lower:
                    perm_error = CommandPermissionError(
                        payload={"stderr": result.stdout}
                    )
                    logger.critical(perm_error.to_log())
                    raise perm_error

                elif (
                    "command not found" in stderr_lower
                    or "no such file" in stderr_lower
                ):
                    dep_miss_error = CommandDependencyMissingError(
                        payload={"stderr": result.stdout}
                    )
                    logger.error(dep_miss_error.to_log())
                    raise dep_miss_error

            if not result.stdout.strip():
                output_error = CommandOutputError(payload={"stdout": result.stdout})
                logger.error(output_error.to_log())
                raise output_error

            return log.parse(result.stdout)

        except subprocess.TimeoutExpired as timeout:
            timeout_error = CommandTimeOutError(
                payload={"command": command, "error": str(timeout)}
            )
            logger.error(timeout_error.to_log)
            raise timeout

        except OSError as e:
            notfound_error = CommandNotFoundError(
                payload={"command": command, "error": str(e)}
            )
            logger.error(notfound_error.to_log())
            raise notfound_error


if __name__ == "__main__":
    print(CommandExecutor().run_command(["mvt-android"]))
