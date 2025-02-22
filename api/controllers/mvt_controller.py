import re
import os
import subprocess
from typing import List, Dict, Union

class MVTController:
    """
    Controller for managing MVT-Android commands.

    This class provides methods to execute `mvt-android` commands such as checking 
    devices connected via ADB and analyzing APK files. Common logic is centralized 
    for better code reuse and maintainability.
    """
    @staticmethod
    def _parse_mvt_output(mvt_log) -> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
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
        # Clean the log output (removes unnecessary information)
        mvt_log = MVTController._clean_mvt_output(mvt_log)
        
        # Handle specific error cases
        if "no devices/emulators found" in mvt_log:
            return {'success': False, 'error': 'O ADB não encontrou nenhum dispositivo'}
        if "device unautorized" in mvt_log:
            return {"success": False, "error": "Dispositivo ADB não autorizado. Verifique a tela do dispositivo para um prompt de confirmação."}

        # Regex pattern to match the log entries
        pattern = re.compile(r"(?P<status>INFO|WARNING|ERROR|CRITICAL)\[.*?\](?P<message>.+)", re.MULTILINE)

        parsed_data = []
        detections = []

        for index, match in enumerate(pattern.finditer(mvt_log)):
            id = index
            status = match.group("status").strip()
            log_message = match.group("message").strip()

            # Store the log entry with id, status, and message
            parsed_data.append({"id":id, "status": status, "message": log_message})

            # If the status is WARNING, detect it for further analysis
            if status == 'WARNING':
                print(log_message)
                detections.append(log_message)

        messages = []

        # Generate a security report for detected vulnerabilities
        if detections:
            messages = MVTController._generate_security_report(detections)
        
        # If no log entries were parsed, return the raw log as an error
        if not parsed_data:
            return {
                "success": False,
                "error": mvt_log
            }

        # Return the structured data including success status, log entries, and security messages
        return {
            "success": not any(item["status"] in ["CRITICAL"] for item in parsed_data),
            "log": parsed_data,
            "messages": messages
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
        """
        reports = []

        # Patterns to identify security issues
        patterns = (
            (r"has not received security updates", "Atualização", "Seu dispositivo pode estar desatualizado! Verifique se há atualizações disponíveis para maior segurança."),
            (r"SELinux status is \"permissive\"", "Configuração de Segurança", "O SELinux está em modo permissivo, reduzindo a proteção do sistema. Considere ativá-lo no modo 'enforcing'."),
            (r"installed package related to rooting/jailbreaking", "Aplicativos Suspeitos", "Aplicativo suspeito detectado. Se não reconhece esse app, remova-o imediatamente."),
            (r"Found root binary", "Acesso Root", "O dispositivo pode estar com root ativo, aumentando os riscos de segurança. Se não fez root de propósito, procure um técnico especializado para corrigir o problema."),
            (r"Detected indicators of compromise", "Indícios de Comprometimento", "Possíveis sinais de ataque detectados! Verifique aplicativos suspeitos e considere uma restauração de fábrica."),
            (r"ADB is enabled", "Depuração ADB", "O modo de depuração ADB está ativado. Isso pode expor seu dispositivo a riscos se estiver conectado a redes não confiáveis. Desative se não for necessário."),
            (r"Untrusted certificates found", "Certificados", "Certificados não confiáveis detectados. Isso pode indicar um ataque MITM (Man-in-the-Middle). Revise os certificados instalados."),
            (r"Suspicious network activity", "Rede", "Atividade de rede suspeita detectada. Verifique suas conexões e considere usar uma VPN para maior segurança."),
            (r"Malware signatures detected", "Malware", "Possível malware encontrado! Execute uma verificação completa com um antivírus confiável."),
            (r"accessibility_enabled = 1", "Acessibilidade Ativada", "O serviço de acessibilidade está ativado. Aplicativos mal-intencionados podem explorar essa função para capturar dados sensíveis. Verifique as permissões concedidas."),
            (r"install_non_market_apps = 1", "Instalação de Apps de Fontes Desconhecidas", "A instalação de aplicativos fora da Google Play Store está ativada. Isso pode permitir a instalação de software malicioso. Desative essa opção se não for necessária."),
        )

        # Checking each warning against predefined patterns
        for warning in warnings:
            for pattern, category, message in patterns:
                if re.search(pattern, warning, re.IGNORECASE):
                    reports.append({"category": category, "message": message})
                    break  # Avoid multiple matches for a single warning

        # If no issues are found, return a clean report
        return reports if reports else [{"category": "Nenhum problema", "message": "Nenhum problema crítico foi encontrado no dispositivo."}]

    @staticmethod
    def _clean_mvt_output(mvt_log)->str:
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
        mvt_log = re.sub(r"(\s+)(?=\S)", ' ', mvt_log)
        mvt_log = re.sub(r"\n+", ' ', mvt_log)
        mvt_log = re.sub(r"(\s+)(INFO|ERROR|CRITICAL|DEBUG|WARNING)(\s+)", r' \2', mvt_log)
        mvt_log = re.sub(r"\s{2,}", ' ', mvt_log)
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
        result = subprocess.run(command, capture_output=True, text=True)

        output = result.stderr if result.stderr else result.stdout

        return MVTController._parse_mvt_output(output)

    @staticmethod
    def check_adb(serial: str = None, 
                  iocs_files: list = None, 
                  output_folder: str = None, 
                  fast: bool = False, 
                  list_modules: bool = False, 
                  module: str = None,
                  non_interactive: bool = False,
                  backup_password: str = None,
                  verbose: bool  = False
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
        command = ['mvt-android', 'check-adb']

        if serial:
            command.extend(['--serial', serial])
        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(['-i', iocs_file])
        if output_folder:
            command.extend(['--output', output_folder])
        if fast:
            command.append('--fast')
        if list_modules:
            command.append('--list-modules')
        if module:
            command.extend(['--module', module])
        if non_interactive:
            command.append('--non-interactive')
        if backup_password:
            command.extend(['--backup-password', backup_password])
        if verbose:
            command.append('--verbose')

        return MVTController._run_command(command)
    
    @staticmethod
    def check_androidqf(androidqf_path: str, 
                        iocs_files: list = None, 
                        output_folder: str = None, 
                        list_modules: bool = False, 
                        module: str = None,
                        hashes: bool = False,
                        non_interactive: bool = False,
                        backup_password: str = None,
                        verbose: bool  = False
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
        command = ['mvt-android', 'check-androidqf', androidqf_path]

        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(['-i', iocs_file])
        if output_folder:
            command.extend(['--output', output_folder])
        if list_modules:
            command.append('--list-modules')
        if module:
            command.extend(['--module', module])
        if hashes:
            command.append('--hashes')
        if non_interactive:
            command.append('--non-interactive')
        if backup_password:
            command.extend(['--backup-password', backup_password])
        if verbose:
            command.append('--verbose')

        return MVTController._run_command(command)

    @staticmethod
    def check_backup(backup_path: str,
                    iocs_files: list = None,
                    output_folder: str = None,
                    list_modules: bool = False,
                    non_interactive: bool = False,
                    backup_password: str = None,
                    verbose: bool = False
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
        command_adb = ['adb', 'backup', '-nocompress', 'com.android.providers.telephony', '-f', backup_path]
        command = ['mvt-android', 'check-backup', backup_path]

        result = MVTController._run_command(command_adb)
        if not result['success'] and 'ADB' in result['error']:
            return result

        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(['-i', iocs_file])
        if output_folder:
            command.extend(['--output', output_folder])
        if list_modules:
            command.append('--list-modules')
        if non_interactive:
            command.append('--non-interactive')
        if backup_password:
            command.extend(['--backup-password', backup_password])
        if verbose:
            command.append('--verbose')

        return MVTController._run_command(command)

    @staticmethod
    def check_bugreport(bugreport_path: str,
                        iocs_files: list = None,
                        output_folder: str = None,
                        list_modules: bool = False,
                        module: str = None,
                        verbose: bool = False
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
        command = ['mvt-android', 'check-bugreport', bugreport_path]

        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(['-i', iocs_file])
        if output_folder:
            command.extend(['--output', output_folder])
        if list_modules:
            command.append('--list-modules')
        if module:
            command.extend(['--module', module])
        if verbose:
            command.append('--verbose')

        return MVTController._run_command(command)

    @staticmethod
    def check_iocs(folder:str=None, 
                   iocs_files:list=None, list_modules:bool=False, 
                   module:str=None
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
            folder = os.path.join(user_home, '.local', 'share', 'mvt', 'indicators')
        
        command = ['mvt-android', 'check-iocs', folder]

        if iocs_files:
            for iocs_file in iocs_files:
                command.extend(['-i', iocs_file])
        if list_modules:
            command.append('--list-modules')
        if module:
            command.extend(['--module', module])
        
        return MVTController._run_command(command)

    @staticmethod
    def download_apks(serial: str = None,
                      all_apks: bool = False,
                      virustotal: bool = False,
                      output_folder: str = None,
                      from_file: str = None,
                      verbose: bool=False
                    )-> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
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
        command = ['mvt-android', 'download-apks']

        if serial:
            command.extend(['--serial', serial])
        if all_apks:
            command.append('--all-apks')
        if virustotal:
            command.append('--virustotal')
        if output_folder:
            command.extend(['--output', output_folder])
        if from_file:
            command.extend(['--from-file', from_file])
        if verbose:
            command.append('--verbose')
        
        return MVTController._run_command(command)
    
    @staticmethod
    def download_iocs()-> Dict[str, Union[bool, str, List[Dict[str, Union[int, str]]]]]:
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
        command = ['mvt-android', 'download-iocs']
        return MVTController._run_command(command)
    