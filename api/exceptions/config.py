class ConfigException(Exception):
    """Exceção base para erros de configuração"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class MissingAPIKeyException(ConfigException):
    """Exceção para quando a chave da API está ausente"""

    def __init__(self):
        super().__init__("Faltou o parâmetro api_key!")


class ConfigWriteError(ConfigException):
    """Exceção para erros ao salvar a configuração"""

    def __init__(self, detail: str = ""):
        message = f"Erro ao salvar variável de ambiente. {detail}"
        super().__init__(message)
