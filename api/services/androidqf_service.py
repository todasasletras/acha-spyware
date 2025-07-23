import uuid

from configuration.settings import BASE_DIR
from core.logger import setup_logger

from api.interfaces.androidqf_interface import AndroidQFInterface
from api.services.command_executor import CommandExecutor

logger = setup_logger(__name__)


class AndroidQF(AndroidQFInterface):
    def __init__(self, executor: CommandExecutor):
        self.BASE_DIR_SCRIPT = f"{BASE_DIR}/scripts"
        self.ANDROIDQF_BINARY = "androidqf"
        self.folder_uuid = str(uuid.uuid4())
        self.backup_maps = {
            "Only SMS": 0,
            "Everything": 1,
            "No Backup": 2,
        }
        self.download_maps = {
            "All": 0,
            "Only no-system packages": 1,
            "Do not download any": 2,
        }
        self.remove_maps = {
            "Yes": 0,
            "No": 1,
        }
        self.executor = executor

    def extract(
        self,
        output_folder: str = "/tmp",
        serial: str | None = None,
        fast: bool = False,
        list_modules: bool = False,
        module: str | None = None,
        verbose: bool = False,
        interactive: bool = True,
        backup_options: str = "Everything",
        download_options: str = "Only no-system packages",
        remove_options: str = "Yes",
    ):
        command = [
            f"{self.BASE_DIR_SCRIPT}/{self.ANDROIDQF_BINARY}",
            "-output",
            f"{output_folder}/{self.folder_uuid}",
        ]
        if serial:
            logger.debug(f"Parametro 'serial' definido: {serial}")
            command.extend(["-serial", serial])
        if fast:
            logger.debug("Parametro 'fast' definido")
            command.append("-fast")
        if list_modules:
            logger.debug("Parametro 'list_modules' definido.")
            command.append("-list")
        if module:
            logger.debug(f"Parametro 'module' definido: {module}")
            command.extend(["-module", module])
        if verbose:
            logger.debug("Parametro 'verbose' definido.")
            command.append("-verbose")

        if not interactive:
            self.executor.run_command(command)

        steps = [
            {
                "expect": "Backup",
                "send": "\x1b[B" * self.backup_maps[backup_options] + "\r",
            },
            {
                "expect": "Download",
                "send": "\x1b[B" * self.download_maps[download_options] + "\r",
            },
            {
                "expect": "Remove",
                "send": "\x1b[B" * self.remove_maps[remove_options] + "\r",
            },
            {
                "expect": "Enter",
                "send": "\r",
            },
        ]

        return self.executor.run_interactive_command(
            command,
            steps,
            commandCWD=self.BASE_DIR_SCRIPT,
        )
