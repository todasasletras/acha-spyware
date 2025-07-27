# Documentação da API – Acha Spyware
## Visão Geral
Esta API é destinada à extração e análise de dados provenientes de dispositivos Android, utilizando a ferramenta Androidqf. Todas as rotas seguem o prefixo /api/ e, por se tratarem de funcionalidades específicas para dispositivos Android, utilizam /api/android/.

## 📁 Endpoints
### 🔹Extração de dados (Androidqf)
- Endpoint: POST /api/android/qf
- Descrição: Realiza a extração de dados de um dispositivo Android utilizando a ferramenta Androidqf.

#### Parâmetros:
| Nome	        | Tipo	         | Padrão	        | Descrição                 |
| :-----------: | :------------: | :--------------: | :------------------------ |
| output_folder	| string	     | "/tmp"	        | Caminho onde os dados extraídos serão armazenados.|
| serial        | string ou null | null	            | Número de série do dispositivo a ser analisado. Se omitido, será selecionado automaticamente.|
| fast      	| boolean        | false        	| Ativa extração rápida.    |
| list_modules	| boolean	     | false        	| Lista os módulos disponíveis para extração.|
| module    	| string ou null | null	            | Nome do módulo específico a ser executado.|
| verbose	    | boolean        | false	        | Exibe logs detalhados da execução.|
| interactive	| boolean    	 | true         	|Habilita modo interativo.  |
| backup_options| string     	 | "Everything"	    |Opções de backup a serem utilizadas. Ex: "Everything", "No-Photos", etc.|
| download_options| string	     | "Only no-system packages"	|Define quais pacotes devem ser baixados.|
| remove_options| string	     | "Yes"	        |Define se os dados serão removidos após extração.|

### 🔸Análise de dados extraídos (Check Androidqf)
- Endpoint: POST /api/android/check-androidqf
- Descrição: Realiza a análise dos dados extraídos anteriormente com base em indicadores de comprometimento (IOCs).

#### Parâmetros:
| Nome	            | Tipo	         | Padrão	    | Descrição                 |
| :---------------: | :------------: | :----------: | :------------------------ |
| androidqf_path	| string	     | Obrigatório  | Caminho para os dados extraídos pelo Androidqf. |
| iocs_files	    | list	         | []           | Lista de arquivos de IOC a serem usados na análise.|
| output_folder	    | string ou null | null	        | Caminho para salvar os resultados da análise.|
| list_modules	    | boolean	     | false	    | Lista os módulos disponíveis para análise.|
| module	        | string ou null | null	        | Executa um módulo específico. |
| hashes	        | boolean	     | false	    | Gera hashes dos arquivos analisados. |
| non_interactive	| boolean	     | false	    | Executa em modo não-interativo.
| backup_password	| string ou null | null	        | Senha para arquivos de backup protegidos.|
| verbose	        | boolean	     | false	    | Exibe logs detalhados da execução.|

