from abc import ABC, abstractmethod


class MVTInterface(ABC):
    @abstractmethod
    def check_backup(
        self,
        backup_path: str,
        iocs_files: list = None,
        output_folder: str = None,
        fast: bool = False,
        list_modules: bool = False,
        non_interactive: bool = False,
        backup_password: str = None,
        verbose: bool = False,
    ): ...

    @abstractmethod
    def check_iocs(
        self,
        folder: str = None,
        iocs_files: list = None,
        list_modules: bool = False,
        module: str = None,
    ): ...

    @abstractmethod
    def download_iocs(self): ...


class MVTAndroidInterface(MVTInterface):
    @abstractmethod
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
    ): ...

    @abstractmethod
    def check_bugreport(
        self,
        bugreport_path: str,
        iocs_files: list = None,
        output_folder: str = None,
        list_modules: bool = False,
        module: str = None,
        verbose: bool = False,
    ): ...

    @abstractmethod
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
    ): ...

    @abstractmethod
    def download_apks(
        self,
        serial: str = None,
        all_apks: bool = False,
        virustotal: bool = False,
        output_folder: str = None,
        from_file: str = None,
        verbose: bool = False,
    ): ...


class MVTIOSInterface(MVTInterface): ...


"""
mvt-android
  check-adb        Check an Android device over ADB
  check-androidqf  Check data collected with AndroidQF
  check-bugreport  Check an Android Bug Report
  download-apks    Download all or only non-system installed APKs

mvt-ios
  check-fs        Extract artifacts from a full filesystem dump
  decrypt-backup  Decrypt an encrypted iTunes backup
  extract-key     Extract decryption key from an iTunes backup


Common
  check-backup     Check an Android Backup
  check-iocs      Compare stored JSON results to provided indicators
  download-iocs   Download public STIX2 indicators
  version         Show the currently installed version of MVT
"""
