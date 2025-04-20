import subprocess
from typing import List

from api.interfaces.command_executor_interface import CommandExecutorInterface
from api.models.types.schemas import LogMessageEntry
from api.exceptions import (
    CommandExecutionError,
    CommandNotFoundError,
    CommandPermissionError,
    CommandTimeOutError,
)
from .log_parser import LogParser

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
                    raise CommandNotFoundError(result.stderr)
                elif "permission denied" in stderr_lower:
                    raise CommandPermissionError(result.stderr)
                if not result.stdout.strip():
                    raise CommandExecutionError(result.stderr)

            return log.parse(result.stdout)

        except subprocess.TimeoutExpired:
            raise CommandTimeOutError(f"TimeOut ao executar o commando: {command}")
        except CommandNotFoundError:
            raise CommandNotFoundError(result.stderr)
        except CommandPermissionError:
            raise CommandPermissionError(result.stderr)
        except Exception as e:
            raise CommandExecutionError(
                f"Erro inesperado ao executar o comando: {command}\n{e}"
            )


if __name__ == "__main__":
    print(CommandExecutor().run_command(["mvt-android", "check-adb"]))
