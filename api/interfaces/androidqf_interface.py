from abc import ABC, abstractmethod


class AndroidQFInterface(ABC):
    @abstractmethod
    def extract(
        self,
        output_folder: str = "/tmp",
        serial: str | None = None,
        fast: bool = False,
        list_modules: bool = False,
        module: str | None = None,
        verbose: bool = False,
        version: bool = False,
    ): ...


"""
// Command line options
serial, "serial", "", "Phone serial number"
output_folder, "output", "", "Output folder"
fast, "fast", false, "Fast mode"
list_modules, "list", false, "List modules and exit"
module, "module", "", "Only execute a specific module"
verbose, "verbose", false, "Verbose mode"
version_flag, "version", false, "Show version"
"""
