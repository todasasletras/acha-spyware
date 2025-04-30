import os

from dotenv import load_dotenv
from api.exceptions.config_except import (
    ConfigFileNotFoundException,
    EncodingErrorException,
    MissingParameterException,
    MissingValueException,
    PermissionDeniedException,
)
from api.interfaces.config_interface import ConfigInterface
from core.logger import setup_logger

logger = setup_logger(__name__)
ENV_FILE = ".env"


class ConfigService(ConfigInterface):
    def set_env_variable(self, var_name, value):
        if not var_name:
            miss_param_error = MissingParameterException("Chave não definido!")
            logger.error(miss_param_error.to_log())
            raise miss_param_error

        if not value:
            miss_value_error = MissingValueException("Chave não definido!")
            logger.error(miss_value_error.to_log())
            raise miss_value_error

        try:
            variable = f"{var_name}={value}\n"

            if not os.path.exists(ENV_FILE):
                with open(ENV_FILE, "w") as file:
                    file.write(variable)

            with open(ENV_FILE, "r+") as file:
                lines = file.readlines()
                file.seek(0)

                for i, line in enumerate(lines):
                    if line.startswith(var_name + "="):
                        lines[i] = variable
                        break
                else:
                    lines.append(variable)

                file.writelines(lines)
                file.truncate()

            os.environ[var_name] = value
            load_dotenv(ENV_FILE)

            return {
                "message": "A chave da API do VirusToatal foi definida com sucesso!"
            }
        except FileNotFoundError as e:
            file_error = ConfigFileNotFoundException({"error": str(e)})
            logger.critical(file_error.to_log())
            raise file_error

        except PermissionError as e:
            perm_error = PermissionDeniedException({"error": str(e)})
            logger.critical(perm_error.to_log())
            raise perm_error

        except UnicodeError as e:
            encoding_error = EncodingErrorException({"error": str(e)})
            logger.critical(encoding_error.to_log())
            raise encoding_error


if __name__ == "__main__":
    config = ConfigService()
    print(config.set_env_variable("teste", "roihtrw873mnfsçocs93qçjkjnsdfkjaee93"))
