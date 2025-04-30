# 🧾 Tabela de Códigos de Erro da API

| Código Numérico | Código                       | Status HTTP | Mensagem para o Cliente                           | Descrição Interna                                                               |
| :-------------: | :--------------------------- | :---------: | :------------------------------------------------ | :------------------------------------------------------------------------------ |
|     `1000`      | `SERVER_UNHANDLED_EXCEPTION` |    `500`    | Ocorreu um erro interno no servidor.              | Unhandled exception no core da aplicação.                                       |
|     `2000`      | `MVT_ANDROID_GENERAL_ERROR`  |    `503`    | Não foi possível executar o MVT-Android.          | Erro genérico no módulo MVT-Android.                                            |
|     `2001`      | `DEVICE_CHECKADB_FAILED`     |    `503`    | Falha ao verificar o dispositivo via ADB.         | Falha ao executar mvt-android check-adb.                                        |
|     `2002`      | `DEVICE_BUSY`                |    `503`    | Dispositivo ocupado durante operação ADB.         | O dispositivo está ocupado. Tente rodar `adb kill-server` e conectar novamente. |
|     `2002`      | `DEVICE_NOT_FOUND`           |    `404`    | Nenhum dispositivo Android foi encontrado.        | Dispositivo não conectado ou não autorizado.                                    |
|     `2003`      | `USB_CONNECTION_FAILED`      |    `503`    | Não foi possível conectar ao dispositivo via USB. | Erro de conexão ADB/USB.                                                        |
|     `2100`      | `MVT_ANDROID_APK_ERROR`      |    `500`    | Erro ao verificar o arquivo APK.                  | Erro ao rodar mvt-android download-apks.                                        |
|     `3000`      | `BACKUP_PATH_INVALID`        |    `400`    | Caminho de backup inválido.                       | O caminho não aponta para um arquivo .ab ou diretório válido.                   |
|     `3001`      | `BACKUP_PASSWORD_MISSING`    |    `400`    | Senha de backup não informada.                    | Parâmetro --backup-password ausente.                                            |
|     `3002`      | `BACKUP_DECRYPTION_FAILED`   |    `422`    | Falha ao descriptografar o backup.                | Senha incorreta ou arquivo de backup corrompido.                                |
|     `3100`      | `CONFIG_NOT_FOUND`           |    `404`    | Configuração não encontrada.                      | Arquivo de configuração ausente ou corrompido.                                  |
|     `3101`      | `CONFIG_INVALID`             |    `400`    | Configuração inválida.                            | Falha de validação das configurações.                                           |
|     `4000`      | `INVALID_INPUT`              |    `422`    | Dados de entrada inválidos.                       | Validação de payload falhou.                                                    |
|     `4001`      | `MISSING_PARAMETER`          |    `400`    | Parâmetro obrigatório ausente.                    | Faltando parâmetro na requisição.                                               |
|     `4002`      | `MISSING_VALUE`              |    `400`    | O valor do parametro está errado.                 | O valor do parametro está vazio ou é inválido.                                  |
|     `4003`      | `PARAMETER_INVALID`          |    `400`    | Parâmetro inválido.                               | O parâmetro fornecido é inválido.                                               |
|     `4104`      | `PERMISSION_DENIED`          |    `403`    | Permissão negada.                                 | Operação não autorizada pelo sistema de arquivos ou dispositivo.                |
|     `4005`      | `CONFIG_FILE_NOT_FOUND`      |    `500`    | Não foi possível definir está configuração.       | O arquivo não foi encontrado.                                                   |
|     `4006`      | `IO_ERROR`                   |    `500`    | Não foi possível definir está configuração.       | Erro de IO para modificar o arquivo.                                            |
|     `4007`      | `ENCODING_ERROR`             |    `500`    | Não foi possível definir está configuração.       | Erro na codificação do arquivo                                                  |
|     `5000`      | `COMMAND_ERROR`              |    `500`    | Não foi possível executar este comando.           | Falha ao executar o comando.                                                    |
|     `5001`      | `COMMAND_NOT_FOUND`          |    `404`    | Comando não encontrado.                           | O comando solicitado não foi localizado no sistema.                             |
|     `5002`      | `COMMAND_TIMEOUT`            |    `408`    | Tempo limite de execução do comando excedido.     | Timeout durante execução do comando.                                            |
|     `5003`      | `COMMAND_PERMISSION_DENIED`  |    `403`    | Permissão negada para executar o comando.         | O usuário ou processo não tem permissão para executar o comando.                |
|     `5004`      | `COMMAND_EXECUTION_FAILED`   |    `500`    | O comando executou com erro.                      | O comando foi executado, mas retornou código diferente de 0.                    |
|     `5005`      | `COMMAND_DEPENDENCY_MISSING` |    `500`    | Dependência ausente para execução do comando.     | Um dos binários necessários para o comando está ausente.                        |
|     `6000`      | `ANALYSIS_PARSE_ERROR`       |    `500`    | Erro ao analisar dados.                           | Falha no parser durante análise.                                                |
|     `6001`      | `PATTERN_FILE_NOT_FOUND`     |    `500`    | Arquivo de padrões não encontrado.                | log_message_patterns.json ausente em api/resources/                             |
|     `6002`      | `INVALID_PATTERN_FORMAT`     |    `500`    | Formato de padrão inválido.                       | Padrão cadastrado em JSON com formato inválido.                                 |
|     `6003`      | `NO_PATTERN_MATCH`           |    `500`    | Resposta inesperado na analise.                   | Padrão não está no JSON.                                                        |
|     `6004`      | `INVALID_REGEX_PATTERN`      |    `500`    | Houve uma falha ao formar a resposta da analise.  | Regex invalido no JSON                                                          |
|     `7000`      | `VT_QUOTA_EXCEEDED`          |    `429`    | Cota da API do VirusTotal excedida.               | Excedido número máximo de requisições à API VT.                                 |
|     `7001`      | `VT_UNEXPECTED_RESPONSE`     |    `502`    | Resposta inesperada do VirusTotal.                | Código de status VT fora do esperado.                                           |
|     `6002`      | `FILE_NOT_FOUND`             |    `404`    | Arquivo não encontrado.                           | Tentativa de acesso a caminho inexistente.                                      |
