from enum import Enum
from typing import TypedDict
from dataclasses import dataclass
from http import HTTPStatus


@dataclass(frozen=True)
class ErrorInfo:
    code: int
    client_message: str
    status_code: HTTPStatus
    internal_message: str


class APIErrorCode(Enum):
    INTERNAL_SERVER_ERROR = ErrorInfo(
        code=1000,
        client_message="Ocorreu um erro interno no servidor.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Unhandled exception no core da aplicação.",
    )
    MVT_ADB_ERROR = ErrorInfo(
        code=2001,
        client_message="Não foi possível verificar o dispositivo.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha ao executar mvt-android check-adb.",
    )
    MVT_APK_ERROR = ErrorInfo(
        code=2002,
        client_message="Erro ao verificar o arquivo APK.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Erro ao rodar mvt-android check-apk.",
    )
    CONFIG_NOT_FOUND = ErrorInfo(
        code=3001,
        client_message="Configuração não encontrada.",
        status_code=HTTPStatus.NOT_FOUND,
        internal_message="Arquivo de configuração ausente ou corrompido.",
    )
    INVALID_INPUT = ErrorInfo(
        code=4000,
        client_message="Dados de entrada inválidos.",
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        internal_message="Validação de payload falhou para campo X.",
    )


class APIExceptionData(TypedDict, total=False):
    message: str
    client_message: str
    status_code: HTTPStatus
    error_code: APIErrorCode
    payload: dict
