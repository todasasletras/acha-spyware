# 🧾 Tabela de Códigos de Erro da API

| Código Numérico | Código                  | Status HTTP | Mensagem para o Cliente                   | Descrição Interna                              |
| :-------------: | :---------------------- | :---------: | :---------------------------------------- | :--------------------------------------------- |
|     `1000`      | `INTERNAL_SERVER_ERROR` |    `500`    | Ocorreu um erro interno no servidor.      | Unhandled exception no core da aplicação.      |
|     `2001`      | `MVT_ADB_ERROR`         |    `500`    | Não foi possível verificar o dispositivo. | Falha ao executar mvt-android check-adb.       |
|     `2002`      | `MVT_APK_ERROR`         |    `500`    | Erro ao verificar o arquivo APK.          | Erro ao rodar mvt-android check-apk.           |
|     `3001`      | `CONFIG_NOT_FOUND`      |    `404`    | Configuração não encontrada.              | Arquivo de configuração ausente ou corrompido. |
|     `4000`      | `INVALID_INPUT`         |    `422`    | Dados de entrada inválidos.               | Validação de payload falhou para campo X.      |
