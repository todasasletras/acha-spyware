from abc import ABC, abstractmethod
from typing import List


class CommandExecutorInterface(ABC):
    @abstractmethod
    def run_command(self, commad: List): ...
