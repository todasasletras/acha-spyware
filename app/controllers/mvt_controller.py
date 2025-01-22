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
    def check_adb(output_dir: str) -> Dict[str, Union[bool, str]]:
        """
        Checks devices connected via ADB using mvt-android.

        Parameters
        ----------
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
        command = ['mvt-android', 'check-adb', '-o', output_dir]
        return MVTController._run_command(command)

    @staticmethod
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
