import os

from dotenv import load_dotenv
from api.interfaces.config_interface import ConfigInterface

ENV_FILE = ".env"


class ConfigService(ConfigInterface):
    def set_env_variable(self, var_name, value):
        if not var_name:
            raise OSError("Chave não definido!")
        if not value:
            raise OSError("Valor não definido!")

        error = ""

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

            message = "A chave da API do VirusToatal foi definida com sucesso!"
        except FileNotFoundError as e:
            message = "Arquivo .env não encontrado."
            error = str(e)

        except PermissionError as e:
            message = "Permissão negada para acessar o arquivo .env."
            error = str(e)

        except (IOError, OSError) as e:
            message = "Erro de leitura ou escrita no arquivo .env."
            error = (str(e),)

        except UnicodeError as e:
            message = "Erro de codificação ao manipular o arquivo .env."
            error = str(e)
        except Exception as e:
            message = "Não foi possível definir a chave da API."
            error = str(e)
        finally:
            response = {"message": message}
            if error:
                response["error"] = error
            return response


if __name__ == "__main__":
    config = ConfigService()
    print(config.set_env_variable("teste", "roihtrw873mnfsçocs93qçjkjnsdfkjaee93"))
