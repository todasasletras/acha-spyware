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
    # ===================== #
    # 1xxx Erro do servidor #
    # ===================== #
    SERVER_UNHANDLED_EXCEPTION = ErrorInfo(
        code=1000,
        client_message="Ocorreu um erro interno no servidor.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Unhandled exception no core da aplicação.",
    )

    # =================================== #
    # 2xx Error ao utilizar o MVT-ANDROID #
    # =================================== #
    MVT_ANDROID_GENERAL_ERROR = ErrorInfo(
        code=2000,
        client_message="Não foi possível executar o MVT-Android.",
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        internal_message="Erro genérico no módulo MVT-Android.",
    )
    DEVICE_CHECKADB_FAILED = ErrorInfo(
        code=2001,
        client_message="Falha ao verificar o dispositivo via ADB.",
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        internal_message="Falha ao executar mvt-android check-adb.",
    )
    DEVICE_BUSY = ErrorInfo(
        code=2003,
        client_message="Dispositivo ocupado durante operação ADB.",
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        internal_message="O dispositivo está ocupado. Tente rodar `adb kill-server` e conectar novamente.",
    )
    DEVICE_NOT_FOUND = ErrorInfo(
        code=2002,
        client_message="Nenhum dispositivo Android foi encontrado.",
        status_code=HTTPStatus.NOT_FOUND,
        internal_message="Dispositivo não conectado ou não autorizado.",
    )
    DEVICE_UNAUTHORIZED: ErrorInfo
    USB_CONNECTION_FAILED = ErrorInfo(
        code=2004,
        client_message="Não foi possível conectar ao dispositivo via USB.",
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        internal_message="Erro de conexão ADB/USB.",
    )
    NETWORK_CONNECTION_FAILED: ErrorInfo

    # ===================================== #
    # Error ao utilizar o MVT [dowloadapks] #
    # ===================================== #
    MVT_ANDROID_APK_ERROR = ErrorInfo(
        code=2100,
        client_message="Erro ao verificar o arquivo APK.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Erro ao rodar mvt-android download-apks.",
    )

    # ===================== #
    # 3xxx – Backup Android #
    # ===================== #
    BACKUP_PATH_INVALID = ErrorInfo(
        code=3000,
        client_message="Caminho de backup inválido.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="O caminho não aponta para um arquivo .ab ou diretório válido.",
    )
    BACKUP_PASSWORD_MISSING = ErrorInfo(
        code=3001,
        client_message="Senha de backup não informada.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="Parâmetro --backup-password ausente.",
    )
    BACKUP_DECRYPTION_FAILED = ErrorInfo(
        code=3002,
        client_message="Falha ao descriptografar o backup.",
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        internal_message="Senha incorreta ou arquivo de backup corrompido.",
    )
    BACKUP_INVALID_FORMAT: ErrorInfo

    # =====================================#
    # 31xx – Configuração
    # =====================================#
    CONFIG_NOT_FOUND = ErrorInfo(
        code=3100,
        client_message="Configuração não encontrada.",
        status_code=HTTPStatus.NOT_FOUND,
        internal_message="Arquivo de configuração ausente ou corrompido.",
    )
    CONFIG_INVALID = ErrorInfo(
        code=3101,
        client_message="Configuração inválida.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="Falha de validação das configurações.",
    )

    # ===================================== #
    # 4xxx – Entrada do Usuário e Permissões
    # ===================================== #
    INVALID_INPUT = ErrorInfo(
        code=4000,
        client_message="Dados de entrada inválidos.",
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        internal_message="Validação de payload falhou.",
    )
    MISSING_PARAMETER = ErrorInfo(
        code=4001,
        client_message="Parâmetro obrigatório ausente.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="Faltando parâmetro na requisição.",
    )
    MISSING_VALUE = ErrorInfo(
        code=4002,
        client_message="O valor do parametro está errado.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="O valor do parametro está vazio ou é inválido.",
    )
    PARAMETER_INVALID = ErrorInfo(
        code=4003,
        client_message="Parâmetro inválido.",
        status_code=HTTPStatus.BAD_REQUEST,
        internal_message="O parâmetro fornecido é inválido.",
    )
    PERMISSION_DENIED = ErrorInfo(
        code=4104,
        client_message="Permissão negada.",
        status_code=HTTPStatus.FORBIDDEN,
        internal_message="Operação não autorizada pelo sistema de arquivos ou dispositivo.",
    )
    CONFIG_FILE_NOT_FOUND = ErrorInfo(
        code=4005,
        client_message="Não foi possível definir está configuração.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="O arquivo não foi encontrado.",
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

    # ============================== #
    # 5xxx – Comandos
    # ============================== #
    COMMAND_ERROR = ErrorInfo(
        code=5000,
        client_message="Não foi possível executar este comando.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha ao executar o comando.",
    )
    COMMAND_NOT_FOUND = ErrorInfo(
        code=5001,
        client_message="Comando não encontrado.",
        status_code=HTTPStatus.NOT_FOUND,
        internal_message="O comando solicitado não foi localizado no sistema.",
    )
    COMMAND_TIMEOUT = ErrorInfo(
        code=5002,
        client_message="Tempo limite de execução do comando excedido.",
        status_code=HTTPStatus.REQUEST_TIMEOUT,
        internal_message="Timeout durante execução do comando.",
    )
    COMMAND_PERMISSION_DENIED = ErrorInfo(
        code=5003,
        client_message="Permissão negada para executar o comando.",
        status_code=HTTPStatus.FORBIDDEN,
        internal_message="O usuário ou processo não tem permissão para executar o comando.",
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
    # 6xxx – Parser / Análise
    # ============================== #
    ANALYSIS_PARSE_ERROR = ErrorInfo(
        code=6000,
        client_message="Erro ao analisar dados.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha no parser durante análise.",
    )
    PATTERN_FILE_NOT_FOUND = ErrorInfo(
        code=6001,
        client_message="Arquivo de padrões não encontrado.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="log_message_patterns.json ausente em api/resources/",
    )
    INVALID_PATTERN_FORMAT = ErrorInfo(
        code=6002,
        client_message="Formato de padrão inválido.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Padrão cadastrado em JSON com formato inválido.",
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

    # ============================== #
    # 7xxx – VirusTotal / IOCs
    # ============================== #
    VT_QUOTA_EXCEEDED = ErrorInfo(
        code=7000,
        client_message="Cota da API do VirusTotal excedida.",
        status_code=HTTPStatus.TOO_MANY_REQUESTS,
        internal_message="Excedido número máximo de requisições à API VT.",
    )
    VT_UNEXPECTED_RESPONSE = ErrorInfo(
        code=7001,
        client_message="Resposta inesperada do VirusTotal.",
        status_code=HTTPStatus.BAD_GATEWAY,
        internal_message="Código de status VT fora do esperado.",
    )

    # =================== #
    # Precisa categorizar #
    # =================== #
    FILE_NOT_FOUND = ErrorInfo(
        code=6002,
        client_message="Arquivo não encontrado.",
        status_code=HTTPStatus.NOT_FOUND,
        internal_message="Tentativa de acesso a caminho inexistente.",
    )
    FOLDER_CREATION_ERROR = ErrorInfo(
        code=6003,
        client_message="Erro ao criar diretório.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha ao criar diretório.",
    )
    MODULE_EXECUTION_ERROR = ErrorInfo(
        code=6004,
        client_message="Erro na execução do módulo.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha ao executar o módulo.",
    )
    ANALYSIS_INDICATOR_INDEX_RETRIEVE_FAILED = ErrorInfo(
        code=6005,
        client_message="Falha ao recuperar o índice de indicadores da análise.",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        internal_message="Falha ao recuperar o índice de indicadores da análise.",
    )


class APIExceptionData(TypedDict, total=False):
    message: str
    client_message: str
    status_code: HTTPStatus
    error_code: APIErrorCode
    payload: dict
