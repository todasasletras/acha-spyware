from abc import ABC, abstractmethod


class MVTInterface(ABC):
    @abstractmethod
    def check_backup(self): ...

    @abstractmethod
    def check_iocs(self): ...

    @abstractmethod
    def download_iocs(self): ...


class MVTAndroidInterface(MVTInterface):
    @abstractmethod
    def check_adb(self): ...

    @abstractmethod
    def check_bugreport(self): ...

    @abstractmethod
    def check_androidqf(self): ...

    @abstractmethod
    def download_apks(self): ...


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
