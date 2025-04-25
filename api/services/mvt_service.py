import os
from typing import List, Dict, Union

from api.exceptions.command_executor import CommandExecutionError
from core.logger import setup_logger
from api.interfaces.mvt_interface import MVTAndroidInterface
from api.services.command_executor import CommandExecutor
from api.models.types.schemas import APIResponse, LogMessageEntry

logger = setup_logger()


class MVTAndroid(MVTAndroidInterface):
    """
    Controller for managing MVT-Android commands.

    This class provides methods to execute `mvt-android` commands such as checking
    devices connected via ADB and analyzing APK files. Common logic is centralized
    for better code reuse and maintainability.
    """

    def __init__(self, executor: CommandExecutor):
        self.executor = executor

    def check_adb(
        self,
        serial: str = None,
        iocs_files: list = None,
        output_folder: str = None,
        fast: bool = False,
        list_modules: bool = False,
        module: str = None,
        non_interactive: bool = False,
        backup_password: str = None,
        verbose: bool = False,
    ) -> LogMessageEntry | APIResponse:
        """
        Checks an Android device over ADB using mvt-android.

        This command analyzes a connected Android device for indicators
        of compromise (IOCs) or other issues.

        Parameters
        ----------
        serial : str, optional
            Specify a device serial number or HOST:PORT connection string.
        iocs_files : list, optional
            A list of paths to indicators files. Can include multiple files.
        output_folder : str
            Specify a path to folder where JSON results will be stored.
        fast : bool, optional
            Skip time/resource-consuming features.
        list_modules : bool, optional
            If true, list availabe modules and exit.
        modules : str, optional
            Name of a single module to run instead of all.
        non_interactive : bool, optional
            Avoid interactive questions during processing.
        backup_password : str, optional
            Backup password to use for an Android backup
        verbose : bool, optional
            if True, enables verbose mode.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical message.
            - 'output' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The serity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'error' (str, optional): The error message.
        """
        command = ["mvt-android", "check-adb"]
        try:
            if serial:
                logger.debug(f"Parametro serial definido: {serial}")
                command.extend(["--serial", serial])
            if iocs_files:
                logger.debug(f"Parametro iocs_files definido: {iocs_files}")
                for iocs_file in iocs_files:
                    command.extend(["-i", iocs_file])
            if output_folder:
                logger.debug(f"Parametro output definido: {output_folder}")
                command.extend(["--output", output_folder])
            if fast:
                logger.debug(f"Parametro fast definido: {fast}")
                command.append("--fast")
            if list_modules:
                logger.debug(f"Parametro list_modules definido: {list_modules}")
                command.append("--list-modules")
            if module:
                logger.debug(f"Parametro module definido: {module}")
                command.extend(["--module", module])
            if non_interactive:
                logger.debug(f"Parametro non-interactive definido: {non_interactive}")
                command.append("--non-interactive")
            if backup_password:
                logger.debug(f"Parametro backup-password definido: {backup_password}")
                command.extend(["--backup-password", backup_password])
            if verbose:
                logger.debug(f"Parametro verbose definido: {verbose}")
                command.append("--verbose")

            return self.executor.run_command(command)
        except CommandExecutionError as e:
            raise e

    def check_androidqf(
        self,
        androidqf_path: str,
        iocs_files: list = None,
        output_folder: str = None,
        list_modules: bool = False,
        module: str = None,
        hashes: bool = False,
        non_interactive: bool = False,
        backup_password: str = None,
        verbose: bool = False,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
        """
        Checks data collected with AndroidQF using mvt-android.

        This command analyzes AndroidQF data for indicators of compromise (IOCs).

        Parameters
        ----------
        androidqf : str
            Path to the AndroidQF data to be analyzed.
        iocs_files : list, optional
            A list of paths to indicators files. Can include multiple files.
        output_folder : str
            Specify a path to folder where JSON results will be stored.
        fast : bool, optional
            Skip time/resource-consuming features.
        list_modules : bool, optional
            If true, list availabe modules and exit.
        modules : str, optional
            Name of a single module to run instead of all.
        hashes : str, optional
            If True, generate hashes of all files analyzed.
        non_interactive : bool, optional
            Avoid interactive questions during processing.
        backup_password : str, optional
            Backup password to use for an Android backup
        verbose : bool, optional
            if True, enables verbose mode.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical message.
            - 'output' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The serity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'error' (str, optional): The error message.
        """
        command = ["mvt-android", "check-androidqf", androidqf_path]

        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(["-i", iocs_file])
        if output_folder:
            command.extend(["--output", output_folder])
        if list_modules:
            command.append("--list-modules")
        if module:
            command.extend(["--module", module])
        if hashes:
            command.append("--hashes")
        if non_interactive:
            command.append("--non-interactive")
        if backup_password:
            command.extend(["--backup-password", backup_password])
        if verbose:
            command.append("--verbose")

        return self.executor.run_command(command)

    def check_backup(
        self,
        backup_path: str,
        iocs_files: list = None,
        output_folder: str = None,
        list_modules: bool = False,
        non_interactive: bool = False,
        backup_password: str = None,
        verbose: bool = False,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
        """
        Checks an Android Backup using mvt-android.

        This command analyzes an Android backup for indicators of compromise (IOCs).

        Parameters
        ----------
        backup_path : str
            Path to the Android backup to be analyzed.
        iocs_files : list, optional
            A list of paths to indicators files. Can include multiple files.
        output_folder : str, optional
            Specify a path to a folder where JSON results will be stored.
        list_modules : bool, optional
            If True, list available modules and exit.
        non_interactive : bool, optional
            Avoid interactive questions during processing.
        backup_password : str, optional
            Backup password to use for decrypting the Android backup.
        verbose : bool, optional
            If True, enables verbose mode.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical message.
            - 'output' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The serity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'error' (str, optional): The error message.
        """
        logger.debug("Inicniando check-backup")
        command_adb = [
            "adb",
            "backup",
            "-nocompress",
            "com.android.providers.telephony",
            "-f",
            backup_path,
        ]
        command_kill_adb = ["adb", "kill-server"]
        command = ["mvt-android", "check-backup", backup_path]

        result = self.executor.run_command(command_adb)
        if not result["success"] and "ADB" in result["error"]:
            logger.warning(result)
            return result

        logger.debug("Finaliza o adb para evitar problemas com os comandos do mvt")
        self.executor.run_command(command_kill_adb)

        if iocs_files:
            logger.debug(f"Parametro iocs-files definido: {iocs_files}")
            for iocs_file in iocs_files:
                command.extend(["-i", iocs_file])
        if output_folder:
            logger.debug(f"Parametro output definido: {output_folder}")
            command.extend(["--output", output_folder])
        if list_modules:
            logger.debug(f"Parametro list-modules definido: {list_modules}")
            command.append("--list-modules")
        if non_interactive:
            logger.debug(f"Parametro non-interactive definido: {non_interactive}")
            command.append("--non-interactive")
        if backup_password:
            logger.debug(f"Parametro backup-password definido: {backup_password}")
            command.extend(["--backup-password", backup_password])
        if verbose:
            logger.debug(f"Parametro verbose definido: {verbose}")
            command.append("--verbose")

        return self.executor.run_command(command)

    def check_bugreport(
        self,
        bugreport_path: str,
        iocs_files: list = None,
        output_folder: str = None,
        list_modules: bool = False,
        module: str = None,
        verbose: bool = False,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
        """
        Checks an Android Bug Report using mvt-android.

        This command analyzes an Android bug report for indicators of compromise (IOCs).

        Parameters
        ----------
        bugreport_path : str
            Path to the Android bug report file to be analyzed.
        iocs_files : list, optional
            A list of paths to indicators files. Can include multiple files.
        output_folder : str, optional
            Specify a path to a folder where JSON results will be stored.
        list_modules : bool, optional
            If True, list available modules and exit.
        module : str, optional
            Name of a single module to run instead of all.
        verbose : bool, optional
            If True, enables verbose mode.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical message.
            - 'output' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The serity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'error' (str, optional): The error message.
        """
        command = ["mvt-android", "check-bugreport", bugreport_path]

        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(["-i", iocs_file])
        if output_folder:
            command.extend(["--output", output_folder])
        if list_modules:
            command.append("--list-modules")
        if module:
            command.extend(["--module", module])
        if verbose:
            command.append("--verbose")

        return self.executor.run_command(command)

    def check_iocs(
        self,
        folder: str = None,
        iocs_files: list = None,
        list_modules: bool = False,
        module: str = None,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
        """
        Compares stored JSON results to provided indicators using mvt-android.

        This command analyzes a folder containing JSON resuts against specifed
        indicators of compromise (IOCs).

        Parameters
        ----------
        folder : str, optional
            the folder containig the JSON results to analyze. Defaults to
            "/home/<user>/.local/share/mvt/indicators/".
        iocs_files : list, optional
            A list of paths to indicators files. Can include multiple files.
        list)modules : bool, optional
            If True, list all available modules and exits.
        module : str, optional
            Specifies the name of a single module to run instead of all.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical message.
            - 'output' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The serity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'error' (str, optional): The error message.
        """
        if not folder:
            user_home = os.path.expanduser("~")
            folder = os.path.join(user_home, ".local", "share", "mvt", "indicators")

        command = ["mvt-android", "check-iocs", folder]

        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(["-i", iocs_file])
        if list_modules:
            command.append("--list-modules")
        if module:
            command.extend(["--module", module])

        return self.executor.run_command(command)

    def download_apks(
        self,
        serial: str = None,
        all_apks: bool = False,
        virustotal: bool = False,
        output_folder: str = None,
        from_file: str = None,
        verbose: bool = False,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
        """
        Downloads APKs from an Android deice using mvt-amdroid.

        This command allows the extraction of APKs from an Android device. with options to include system packages or check packages on VirusTotal.

        Parameters
        ----------
        serial : str, optional
            Specify a device serial number or HOST:PORT connection string
        all_apks : bool, optional
            Extract all packeges installed on the phone, including system packages
        virustotal : bool, optional
            Check packages on VirusTotal
        output_dir: str
            Specify a path to a folder where APKs will be stored.
        from_file : str, optional
            Instead of acquiring from phone, load an existing packages.jos file for lookups (mainly for debugging purposes)
        verbose : bool, optional
            Enable Verbose mode for more detailed output.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical message.
            - 'output' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The serity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'error' (str, optional): The error message.
        """
        command = ["mvt-android", "download-apks"]

        if serial:
            command.extend(["--serial", serial])
        if all_apks:
            command.append("--all-apks")
        if virustotal:
            command.append("--virustotal")
        if output_folder:
            command.extend(["--output", output_folder])
        if from_file:
            command.extend(["--from-file", from_file])
        if verbose:
            command.append("--verbose")

        return self.executor.run_command(command)

    def download_iocs(
        self,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
        """
        Downloads public STIX2 indicators using mvt-amdroid.

        This command downloads the latest puplic STIX2 indicatores for analysis.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical message.
            - 'output' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The serity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'error' (str, optional): The error message.
        """
        logger.debug("Iniciando download-iocs")
        command = ["mvt-android", "download-iocs"]
        logger.debug("Executando comando")
        result = self.executor.run_command(command)
        if not result["success"]:
            logger.warning("Atualização dos IOCs nao realizada.")
            return {
                "success": result["success"],
                "error": "Não foi possível atualizar IOCs.",
            }

        messages = {
            "category": "Atualização IOCs",
            "message": "Atualização concluída com sucesso!",
        }
        result["messages"] = messages
        return result
