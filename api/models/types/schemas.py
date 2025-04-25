from enum import Enum
from typing import TypedDict, List

from api.models.types.exception import APIErrorCode


class CategoryType(str, Enum):
    ERROR_ANALYSIS = "Erro na Análise"
    POSSIBLE_ATTACK = "Possível Invasão"
    SUSPICIOUS_APP = "Aplicativos Suspeitos"
    SYSTEM_SECURITY = "Segurança do Sistema"
    INFORMATION = "Informativo"
    VIRUSTOTAL = "VirusTotal"
    STALKING = "Stalking"


class MessageLogType(TypedDict):
    pattern: str
    is_regex: bool
    category: CategoryType
    message: str


class LogStatus(str, Enum):
    NONE = "-"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(TypedDict):
    id: int
    status: LogStatus
    message: str


class MessageEntry(TypedDict):
    category: CategoryType
    message: str
    original_message: str


class LogMessageEntry(TypedDict):
    logs: List[LogEntry]
    messages: List[MessageEntry]


class APIResponse(LogMessageEntry, total=False):
    success: bool
    error: str
    code: APIErrorCode
