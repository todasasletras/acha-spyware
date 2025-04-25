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
    # ==================#
    # Erro do servidor #
    # ==================#
    INTERNAL_SERVER_ERROR = ErrorInfo(
        code=1000,
        client_message="Ocorreu um erro interno no servidor.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Unhandled exception no core da aplicação.",
    )

    # MVT
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

    # ==================#
    # Entrada invalida #
    # ==================#
    INVALID_INPUT = ErrorInfo(
        code=4000,
        client_message="Dados de entrada inválidos.",
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        internal_message="Validação de payload falhou para campo X.",
    )

    # =========#
    # Comando #
    # =========#
    COMMAND_NOT_FOUND = ErrorInfo(
        code=5001,
        client_message="Comando não encontrado.",
        status_code=HTTPStatus.NOT_FOUND,
        internal_message="O comando solicitado não foi localizado no sistema.",
    )

    COMMAND_PERMISSION_DENIED = ErrorInfo(
        code=5002,
        client_message="Permissão negada para executar o comando.",
        status_code=HTTPStatus.FORBIDDEN,
        internal_message="O usuário ou processo não tem permissão para executar o comando.",
    )

    COMMAND_TIMEOUT = ErrorInfo(
        code=5003,
        client_message="A execução do comando excedeu o tempo limite.",
        status_code=HTTPStatus.REQUEST_TIMEOUT,
        internal_message="Timeout durante execução do comando. Pode indicar travamento ou lentidão no sistema.",
    )

    COMMAND_EXECUTION_FAILED = ErrorInfo(
        code=5004,
        client_message="O comando executou com erro.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="O comando foi executado, mas retornou código diferente de 0.",
    )

    COMMAND_DEPENDENCY_MISSING = ErrorInfo(
        code=5005,
        client_message="Dependência ausente para execução do comando.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Um dos binários necessários para o comando está ausente.",
    )


class APIExceptionData(TypedDict, total=False):
    message: str
    client_message: str
    status_code: HTTPStatus
    error_code: APIErrorCode
    payload: dict
