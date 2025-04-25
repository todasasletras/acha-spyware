import re
import os
import subprocess
from typing import List, Dict, Union

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

from api.config import logger
from api.exceptions.base import APIException
from api.models.types.schemas import APIResponse, LogMessageEntry
from api.services.command_executor import CommandExecutor
from api.services.mvt_service import MVTAndroid

ENV_FILE = ".env"
logger.debug("Carregar variáveis de ambiente")
load_dotenv()

android_bp = Blueprint("android", __name__, url_prefix="/android")


@android_bp.route("/check-adb", methods=["POST"])
def check_adb():
    try:
        data = request.json
        mvt_android = MVTAndroid(CommandExecutor())
        result: LogMessageEntry = mvt_android.check_adb(**data)
        response: APIResponse = {
            "success": True,
            "logs": result["logs"],
            "messages": result["messages"],
        }
        return jsonify(response), 200
    except APIException as e:
        return jsonify(e.to_dict())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


class MVTController:
    """
    Controller for managing MVT-Android commands.

    This class provides methods to execute `mvt-android` commands such as checking
    devices connected via ADB and analyzing APK files. Common logic is centralized
    for better code reuse and maintainability.
    """

    @staticmethod
    def _parse_mvt_output(
        mvt_log,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
        """
        Parses the MVT (Mobile Verification Toolkit) log output to extract meaningful information.

        This method processes the raw MVT log, extracts relevant details about the status and messages
        in the log, and returns structured information indicating the success of the operation and any
        vulnerabilities detected.

        Parameters
        ----------
        mvt_log : str
            The raw log output from MVT.

        Returns
        -------
        Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]
            A dictionary containing:
            - 'success' (bool): Indicates if the log contains errors or critical messages.
            - 'log' (list, optional): A list of dictionaries, each containing:
                - 'id' (int): A unique identifier for each log entry.
                - 'status' (str): The severity level (INFO, WARNING, ERROR, CRITICAL).
                - 'message' (str): The log message.
            - 'messages' (list, optional):
                - 'category' (str): The categorization of the vulnerability.
                - 'message' (str): The message about the vulnerability.
            - 'error' (str, optional): The error message, if any.
        """
        logger.debug("Clean the log output (removes unnecessary information)")
        mvt_log = MVTController._clean_mvt_output(mvt_log)

        logger.debug("Handle specific error cases")
        no_devices_found_message = "Nenhum dispositivo encontrado. Conecte seu tipositivo via USB e ative o modo desenvolvedor."
        if "no devices/emulators found" in mvt_log:
            logger.warning("Dispositivo não encontrado pelo ADB")
            return {"success": False, "error": no_devices_found_message}
        if "device unautorized" in mvt_log:
            logger.warning("Dispositivo não permite o uso do ADB")
            return {
                "success": False,
                "error": "Dispositivo ADB não autorizado. Verifique a tela do dispositivo para um prompt de confirmação.",
            }
        if "No device found." in mvt_log:
            logger.warning("Dispositivo não encontrado")
            return {"success": False, "error": no_devices_found_message}
        if "Unable to find dumpstate file." in mvt_log:
            logger.warning("Arquivos não encontrado para analise.")
            return {
                "success": False,
                "error": "Não encontramos o arquivo necessário para analisar o problema.",
            }

        logger.debug("Regex pattern to match the log entries")
        pattern = re.compile(
            r"(?P<status>INFO|WARNING|ERROR|CRITICAL)\[.*?\](?P<message>.+)",
            re.MULTILINE,
        )

        parsed_data = []
        detections = []

        for index, match in enumerate(pattern.finditer(mvt_log)):
            id = index
            status = match.group("status").strip()
            log_message = match.group("message").strip()
            logger.debug(
                f"Analise do log: id: {id}, status: {status}, log message: {log_message}"
            )

            logger.debug("Store the log entry with id, status, and message")
            parsed_data.append({"id": id, "status": status, "message": log_message})

            logger.debug(
                "If the status is 'INFO', 'WARNING', 'ERROR', 'CRITICAL', detect it for further analysis"
            )
            if status in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
                detections.append(log_message)

        logger.debug("Generate a security report for detected vulnerabilities")
        messages = MVTController._generate_security_report(detections)

        logger.debug("If no log entries were parsed, return the raw log as an error")
        if not parsed_data:
            logger.warning(f"Erro ao analisar o dispositivo:\n{mvt_log}")
            return {"success": False, "error": mvt_log}

        logger.debug(
            "Return the structured data including success status, log entries, and security messages"
        )
        return {
            "success": not any(item["status"] in ["CRITICAL"] for item in parsed_data),
            "log": parsed_data,
            "messages": messages,
        }

    @staticmethod
    def _generate_security_report(warnings: List[str]) -> List[Dict[str, str]]:
        """
        Generates a security report based on detected warnings.

        This method checks each warning message against predefined patterns to
        classify security risks and provide relevant recommendations.

        Parameters
        ----------
        warnings : List[str]
            A list of warning messages detected during the security scan.

        Returns
        -------
        List[Dict[str, str]]
            A list of dictionaries containing the category and security message for each detected issue.
                A dictionary containing:
                - category (str): A category to classificate the found vulnerabilites.
                - message (str): A message with explanation.
                - original_message (str, optional): The original message about vulnerabilite.
        """
        reports = []

        logger.debug("Patterns to identify security issues")
        patterns = (
            # Atualizações e Segurança do Sistema
            (
                r"has not received security updates",
                "Segurança do Sistema",
                "Seu dispositivo não recebe atualizações há muito tempo. Atualize para maior proteção.",
            ),
            (
                r"SELinux status is \"permissive\"",
                "Segurança do Sistema",
                "A proteção do sistema está reduzida. Ative o SELinux no modo 'enforcing' para mais segurança.",
            ),
            # Aplicativos e Permissões Suspeitas
            (
                r"installed package related to rooting/jailbreaking",
                "Aplicativos Suspeitos",
                "Foi encontrado um aplicativo associado a root ou jailbreak. Remova se não reconhecer.",
            ),
            (
                r"Found root binary",
                "Aplicativos Suspeitos",
                "O dispositivo pode estar com root ativo, aumentando os riscos. Se não fez root intencionalmente, procure um técnico.",
            ),
            (
                r"accessibility_enabled = 1",
                "Aplicativos Suspeitos",
                "Aplicativos podem ter acesso excessivo ao sistema via permissões de acessibilidade. Revise as permissões.",
            ),
            (
                r"install_non_market_apps = 1",
                "Aplicativos Suspeitos",
                "Seu dispositivo permite instalar apps de fora da loja oficial. Isso pode ser arriscado. Desative se não for necessário.",
            ),
            # Possíveis Ameaças e Comprometimentos
            (
                r"Detected indicators of compromise",
                "Possível Invasão",
                "Sinais de ataque detectados! Revise aplicativos suspeitos e considere restaurar o sistema.",
            ),
            (
                r"Malware signatures detected",
                "Possível Invasão",
                "Indícios de malware encontrados! Execute um antivírus para verificar o dispositivo.",
            ),
            (
                r"Untrusted certificates found",
                "Possível Invasão",
                "Foram encontrados certificados não confiáveis, o que pode indicar um ataque. Revise suas configurações.",
            ),
            (
                r"Suspicious network activity",
                "Possível Invasão",
                "Atividade de rede suspeita detectada. Revise conexões e considere usar uma VPN.",
            ),
            # Riscos de Configuração
            (
                r"ADB is enabled",
                "Configuração Insegura",
                "O modo de desenvolvedor (ADB) está ativado. Isso pode expor seu dispositivo a invasões. Desative se não precisar.",
            ),
            # Erros e Problemas Gerais
            (
                r"Unable to find dumpstate file.",
                "Erro na Análise",
                "Não foi possível encontrar um arquivo necessário para a análise. Tente novamente.",
            ),
            (
                r"Invalid backup format, file should be in .ab format",
                "Erro na Análise",
                "O formato do backup está incorreto. Certifique-se de usar um arquivo .ab válido.",
            ),
            (
                r"Device is busy",
                "Erro na Análise",
                "Parece que o dispositivo está ocupado. Tente desconectar e reconectar o dispositivo.",
            ),  # Precisa criar medidas para esse problema
        )

        logger.debug("Checking each warning against predefined patterns")
        for warning in warnings:
            for pattern, category, message in patterns:
                if re.search(pattern, warning, re.IGNORECASE):
                    logger.info(f"Padrao encontrado: {warning}")
                    reports.append(
                        {
                            "category": category,
                            "message": message,
                            "original_message": warning,
                        }
                    )
                    break

        logger.debug("If no issues are found, return a clean report")
        return (
            reports
            if reports
            else [
                {
                    "category": "Nenhum problema",
                    "message": "Nenhum problema crítico foi encontrado no dispositivo.",
                }
            ]
        )

    @staticmethod
    def _clean_mvt_output(mvt_log) -> str:
        """
        Cleans and formats the raw MVT log output for easier processing.

        Parameters
        ----------
        mvt_log : str
            The raw log output from MVT.

        Returns
        -------
        str
            A cleaned and structured version of the log output.
        """
        logger.debug("Padrao regex para limpara a saida do comando mvt")
        mvt_log = re.sub(r"(\s+)(?=\S)", " ", mvt_log)
        mvt_log = re.sub(r"\n+", " ", mvt_log)
        mvt_log = re.sub(
            r"(\s+)(INFO|ERROR|CRITICAL|DEBUG|WARNING)(\s+)", r" \2", mvt_log
        )
        mvt_log = re.sub(r"\s{2,}", " ", mvt_log)
        mvt_log = re.sub(r"(\s)(INFO|ERROR|CRITICAL|DEBUG|WARNING)", r"\1\n\2", mvt_log)

        return mvt_log

    @staticmethod
    def _run_command(command: list) -> Dict[str, Union[bool, str]]:
        """
        Executes a shell command using subprocess and returns the result.

        Parameters
        ----------
        command : list
            The command to be executed, represented as a list of strings.

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
        logger.info(f"Executando o comando: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)

        output = result.stderr if result.stderr else result.stdout

        return MVTController._parse_mvt_output(output)

    @staticmethod
    def check_adb(
        serial: str = None,
        iocs_files: list = None,
        output_folder: str = None,
        fast: bool = False,
        list_modules: bool = False,
        module: str = None,
        non_interactive: bool = False,
        backup_password: str = None,
        verbose: bool = False,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
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

        return MVTController._run_command(command)

    @staticmethod
    def check_androidqf(
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

        return MVTController._run_command(command)

    @staticmethod
    def check_backup(
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

        result = MVTController._run_command(command_adb)
        if not result["success"] and "ADB" in result["error"]:
            logger.warning(result)
            return result

        logger.debug("Finaliza o adb para evitar problemas com os comandos do mvt")
        MVTController._run_command(command_kill_adb)

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

        return MVTController._run_command(command)

    @staticmethod
    def check_bugreport(
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

        return MVTController._run_command(command)

    @staticmethod
    def check_iocs(
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

        return MVTController._run_command(command)

    @staticmethod
    def download_apks(
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

        return MVTController._run_command(command)

    @staticmethod
    def download_iocs() -> Dict[
        str, Union[bool, str, List[Dict[str, Union[int, str]]]]
    ]:
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
        result = MVTController._run_command(command)
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
