from abc import ABC, abstractmethod
from typing import Dict


class ConfigInterface(ABC):
    @abstractmethod
    def set_env_variable(self, var_name: str, value: str) -> Dict[str, str]:
        pass
