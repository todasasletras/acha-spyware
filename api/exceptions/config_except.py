from api.exceptions.base import APIException
from api.models.types.exception import APIErrorCode


class ConfigException(APIException):
    """Exceção base para erros de configuração."""

    pass


class MissingParameterException(ConfigException):
    """Exceção para quando a chave da API está ausente."""

    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.MISSING_PARAMETER, payload=payload)


class ParamenterInvalid(ConfigException):
    def __init__(self, payload=...):
        super().__init__(error=APIErrorCode.PARAMETER_INVALID, payload=payload)


class MissingValueException(ConfigException):
    """Exceção para quando um valor obrigatório está faltando."""

    def __init__(self, field_name, payload: dict = {}):
        super().__init__(
            error=APIErrorCode.MISSING_VALUE, payload={"field": field_name, **payload}
        )


class ConfigFileNotFoundException(ConfigException):
    """Exceção para arquivo .env não encontrado."""

    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.CONFIG_FILE_NOT_FOUND, payload=payload)


class PermissionDeniedException(ConfigException):
    """Exceção para permissão negada ao acessar o arquivo .env."""

    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.PERMISSION_DENIED, payload=payload)


class IOErrorException(ConfigException):
    """Exceção para erro de leitura ou escrita."""

    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.IO_ERROR, payload=payload)


class EncodingErrorException(ConfigException):
    """Exceção para erro de codificação."""

    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.ENCODING_ERROR, payload=payload)
