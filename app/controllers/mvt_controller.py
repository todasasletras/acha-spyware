import os
import subprocess
from typing import Dict, Union

class MVTController:
    """
    Controller for managing MVT-Android commands.

    This class provides methods to execute `mvt-android` commands such as checking 
    devices connected via ADB and analyzing APK files. Common logic is centralized 
    for better code reuse and maintainability.
    """

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
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'success' (bool): Indicates if the command executed successfully.
            - 'stdout' (str, optional): Standard output if the command succeeds.
            - 'stderr' (str, optional): Standard error if the command fails.
        """
        result = subprocess.run(command, capture_output=True, text=True)
        if result.stdout:
            return {'success': True, 'stdout': result.stdout}
        else:
            return {'success': False, 'stderr': result.stderr}

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
                ) -> Dict[str, Union[bool, str]]:
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
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'success' (bool): Indicates if the command executed successfully.
            - 'stdout' (str, optional): Standard output if the command succeeds.
            - 'stderr' (str, optional): Standard error if the command fails.
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
                ) -> Dict[str, Union[bool, str]]:
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
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'success' (bool): Indicates if the command executed successfully.
            - 'stdout' (str, optional): Standard output if the command succeeds.
            - 'stderr' (str, optional): Standard error if the command fails.
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
                ) -> Dict[str, Union[bool, str]]:
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
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'success' (bool): Indicates if the command executed successfully.
            - 'stdout' (str, optional): Standard output if the command succeeds.
            - 'stderr' (str, optional): Standard error if the command fails.
        """
        command = ['mvt-android', 'check-backup', backup_path]

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

    @staticmethod # This command not exist
    def check_apk(file_path: str, output_dir: str) -> Dict[str, Union[bool, str]]:
        """
        Analyzes an APK file using mvt-android.

        Parameters
        ----------
        file_path : str
            The path to the APK file to be analyzed.
        output_dir : str
            The directory where the output of the command will be saved.

        Returns
        -------
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'success' (bool): Indicates if the command executed successfully.
            - 'stdout' (str, optional): Standard output if the command succeeds.
            - 'stderr' (str, optional): Standard error if the command fails.
        """
        command = ['mvt-android', 'check-apk', '-i', file_path, '-o', output_dir]
        return MVTController._run_command(command)

    @staticmethod
    def check_iocs(folder:str=None, iocs_files:list=None, list_modules:bool=False, module:str=None) -> Dict[str, Union[bool, str]]:
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
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'success' (bool): Indicates if  the commmand executed seccessfully.
            - 'stdout' (str, optional): Standard output if the command succeeds.
            - 'stderr' (str, optional): Standard error if the command fails.
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
    def download_iocs()-> Dict[str, Union[bool, str]]:
        """
        Downloads the latest Indicators of Compromise (IOCs) using mvt-amdroid.

        Returns
        -------
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'succes' (bool): IIndicates if the command executed successfuly.
            - 'stdout' (str, optional): Standard outputif the command successds.
            - 'stderr' (str, optional): Standard error if the command fails.
        """
        command = ['mvt-android', 'download-iocs']
        return MVTController._run_command(command)
    
    @staticmethod
    def download_apks(output_dir: str, analyze: bool=False)-> Dict[str, Union[bool, str]]:
        """
        Downloads the latest Indicators of Compromise (IOCs) using mvt-amdroid.

        Parameters
        ----------
        output_dir: str
            The directory where the APKs will be saved.
        analyze : bool, optional
            If True, analyze APks using VirusTotal and other methods.
            Defauts to False.

        Returns
        -------
        Dict[str, Union[bool, str]]
            A dictionary containing:
            - 'succes' (bool): IIndicates if the command executed successfuly.
            - 'stdout' (str, optional): Standard outputif the command successds.
            - 'stderr' (str, optional): Standard error if the command fails.
        """
        command = ['mvt-android', 'download-apks', '-o', output_dir]
        if analyze:
            command.append('-a')
            command.append('-v')
        return MVTController._run_command(command)
