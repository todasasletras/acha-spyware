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
    # ================ #
    # Erro do servidor #
    # ================ #
    INTERNAL_SERVER_ERROR = ErrorInfo(
        code=1000,
        client_message="Ocorreu um erro interno no servidor.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Unhandled exception no core da aplicação.",
    )

    # =============================== #
    # Error ao utilizar o MVT-ANDROID #
    # =============================== #
    MVT_ANDROID_ERROR = ErrorInfo(
        code=2000,
        client_message="Não foi possível executar o MVT-Android.",
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        internal_message="Falha ao executar o MVT-Android.",
    )
    # ================================== #
    # Error ao utilizar o MVT [checkADB] #
    # ================================== #
    MVT_ANDROID_CHECKADB_ERROR = ErrorInfo(
        code=2100,
        client_message="Não foi possível verificar o dispositivo.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha ao executar mvt-android check-adb.",
    )
    MVT_ANDROID_CHECKADB_NOT_FOUND = ErrorInfo(
        code=2101,
        client_message="Não foi possível encontrar o dispositivo.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Dispositivo não encontrado.",
    )

    # ================================== #
    # Error ao utilizar o MVT [dowloadapks] #
    # ================================== #
    MVT_ANDROID_APK_ERROR = ErrorInfo(
        code=2200,
        client_message="Erro ao verificar o arquivo APK.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Erro ao rodar mvt-android check-apk.",
    )

    # =====================================#
    # Erro na definição das configurações #
    # =====================================#
    CONFIG_ERROR = ErrorInfo(
        code=3000,
        client_message="Não foi possível definir está configuração",
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        internal_message="Falha ao definir a configuração",
    )
    CONFIG_NOT_FOUND = ErrorInfo(
        code=3001,
        client_message="Configuração não encontrada.",
        status_code=HTTPStatus.NOT_FOUND,
        internal_message="Arquivo de configuração ausente ou corrompido.",
    )

    # ===================================== #
    # Erro relacionado ao pedido do usuário #
    # ===================================== #
    INVALID_INPUT = ErrorInfo(
        code=4000,
        client_message="Dados de entrada inválidos.",
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        internal_message="Validação de payload falhou para campo X.",
    )
    MISSING_PARAMETER = ErrorInfo(
        code=4001,
        client_message="Precisa fornecer parametros para essa requisição.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="Está faltando parametro na requisição.",
    )
    PARAMETER_INVALID = ErrorInfo(
        code=4002,
        client_message="Precisa fornecer o parametros correto para esta requisição.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="O parametro utilizado é invalido.",
    )
    MISSING_VALUE = ErrorInfo(
        code=4003,
        client_message="O valor do parametro está errado.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="O valor do parametro está vazio ou é inválido.",
    )
    CONFIG_FILE_NOT_FOUND = ErrorInfo(
        code=4004,
        client_message="Não foi possível definir está configuração.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="O arquivo não foi encontrado.",
    )
    PERMISSION_DENIED = ErrorInfo(
        code=4005,
        client_message="Não foi possível definir está configuração.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Permissão negada para editar o arquivo",
    )
    IO_ERROR = ErrorInfo(
        code=4006,
        client_message="Não foi possível definir está configuração.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Erro de IO para modificar o arquivo.",
    )
    ENCODING_ERROR = ErrorInfo(
        code=4007,
        client_message="Não foi possível definir está configuração.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Erro na codificação do arquivo",
    )

    # ================================#
    # Definição de Comandos invalidos #
    # ================================#
    COMMAND_ERROR = ErrorInfo(
        code=5000,
        client_message="Não foi possível executar este comando.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha ao executar o comando",
    )
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

    # ============================== #
    # Erros relacionados aos parsers #
    # ============================== #
    PARSER_ERROR = ErrorInfo(
        code=6000,
        client_message="Erro ao obter informações na analise.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Não é possível fazer o parser no JSON.",
    )
    PATTERN_FILE_NOT_FOUND = ErrorInfo(
        code=6001,
        client_message="Não é possível criar resposta para a analise.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Arquivo 'log_message_patterns.json' não encontrado em 'api/resources/'",
    )
    INVALID_PATTERN_FORMAT = ErrorInfo(
        code=6002,
        client_message="Houve uma falha ao formar a resposta da analise.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Formato do padrão é invalido.",
    )
    NO_PATTERN_MATCH = ErrorInfo(
        code=6003,
        client_message="Resposta inesperado na analise.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Padrão não está no JSON.",
    )
    INVALID_REGEX_PATTERN = ErrorInfo(
        code=6004,
        client_message="Houve uma falha ao formar a resposta da analise.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Regex invalido no JSON",
    )


class APIExceptionData(TypedDict, total=False):
    message: str
    client_message: str
    status_code: HTTPStatus
    error_code: APIErrorCode
    payload: dict
