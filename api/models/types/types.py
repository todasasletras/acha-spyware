from enum import Enum
from dataclasses import dataclass
from typing import TypedDict, List


class CategoryType(str, Enum):
    ERROR_ANALYSIS = "Erro na Análise"
    POSSIBLE_ATTACK = "Possível Invasão"
    SUSPICIOUS_APP = "Aplicativos Suspeitos"
    SYSTEM_SECURITY = "Segurança do Sistema"
    INFORMATION = "Informativo"
    VIRUSTOTAL = "VirusTotal"


class MessageLogType(TypedDict):
    pattern: str
    is_regex: bool
    category: CategoryType
    message: str


class LogStatus(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEntry(TypedDict):
    id: int
    status: LogStatus
    message: str


class MessageEntry(TypedDict):
    category: CategoryType
    message: str
    original_message: str


class APIResponse(TypedDict, total=False):
    success: bool
    log: List[LogEntry]
    messages: MessageEntry
    error: str
