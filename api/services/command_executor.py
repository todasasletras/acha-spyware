from typing import List, Dict

import subprocess
import pexpect
import uuid

from api.interfaces.command_executor_interface import CommandExecutorInterface
from api.models.types.schemas import (
    LogMessageEntry,
    LogEntry,
    MessageEntry,
    LogStatus,
    CategoryType,
)
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
    def run_interactive_command(
        self, command, interaction_steps: List[Dict], commandCWD=None, timeout=2000
    ) -> LogMessageEntry:
        logger.debug(
            f"Executing interactive command: {' '.join(command)} and cwd: {commandCWD}"
        )
        child = pexpect.spawn(" ".join(command), cwd=commandCWD)

        try:
            for step in interaction_steps:
                logger.debug(f"Waiting for prompt: {step['expect']}")
                child.expect(step["expect"], timeout=timeout)
                logger.debug(f"Sending response: {step['send']}")
                child.sendline(step["send"])
            else:
                logger.debug("Waiting for command to finish...")

            child.expect(pexpect.EOF, timeout=None)
            output = child.before.decode("utf-8")
            logger.debug(f"Command output: {output}")
            return LogMessageEntry(
                logs=[
                    LogEntry(id=1, status=LogStatus.INFO, message=output.splitlines())
                ],
                messages=[
                    MessageEntry(
                        category=CategoryType.INFORMATION,
                        message="Extração concluída com sucesso.",
                        original_message=output,
                    ),
                    MessageEntry(
                        category=CategoryType.INFORMATION,
                        message=f"Os dados foram salvos em {command[2]}.",
                        original_message=command[2],
                    ),
                ],
            )
        except pexpect.TIMEOUT as e:
            logger.error(f"[INTERACTIVE] Timeout ao executar comando: {e}")
            return LogMessageEntry(
                logs=[],
                messages=[
                    MessageEntry(
                        category=CategoryType.ERROR_ANALYSIS,
                        message=f"Timeout ao executar comando interativo: {str(e)}",
                        original_message=str(e),
                    )
                ],
            )
        except pexpect.ExceptionPexpect as e:
            # Definir class de exceção personalizada para erros de pexpect
            logger.error(f"[INTERACTIVE] Falha ao executar comando interativo: {e}")
            return LogMessageEntry(
                logs=[],
                messages=[
                    MessageEntry(
                        category=CategoryType.ERROR_ANALYSIS,
                        message=f"Erro ao executar comando interativo: {str(e)}",
                        original_message=str(e),
                    )
                ],
            )

    def run_command(self, command) -> List[LogMessageEntry]:
        logger.debug(f"Executing command: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error(
                    f"Command failed with return code {result.returncode}: {result.stderr}"
                )
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
