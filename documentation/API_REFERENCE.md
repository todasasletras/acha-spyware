# API Detecção de Spyware

## Introdução

A API **Detecção de Spyware** tem como objetivo principal atuar como uma intermediária entre a interface gráfica do usuário (GUI) e a ferramenta **Mobile Verification Toolkit (MVT)**, eliminando a necessidade de interação direta com o terminal.

O **MVT** é uma ferramenta poderosa usada para analisar dispositivos móveis em busca de possíveis indícios de spyware ou ameaças à segurança. No entanto, seu uso pode ser complexo para usuários sem experiência com linha de comando. A API facilita esse processo, fornecendo uma interface acessível e simplificada para executar as funcionalidades do MVT diretamente através de uma aplicação GUI ou qualquer outro cliente que sonsuma os endpoints expostos.

## Principais funcionalidades

A API permite que os usuários realizem operaçõs essenciais do MVT, incluindo:

- **Análise de dispositivos Andorid** para detecção de spyware.
- **Coleta e processamento de logs** para inspeção detalhada de atividades suspeitas. <!-- Precisa melhorar -->
- **Geração de relatórios** organizados e estruturados com os resultados da análise. <!-- Precisa criar -->
- **Automação de processos,** reduzindo erros e simplificando a interação com a ferramenta.

## Publico-Alvo

Esta API é ideal para:

- **Profissionais de segurança cibernética** que precisam analisar dispositivos de forma automatizada.
- **Pesquisadores de segurança** que desejam integrar o MVT a um fluxo de trabalho mais acessível.
- **Usuários preocupados com privacidade**, que desejam uma forma simplificada de verificar se seus dispositivos foram comprometidos.

## Tecnologias Utilizadas

- **Python**: Linguagem principal para processamento e comunicação com o MVT.
- **Flask**: Framework para construção da API.
- **Mobile Verification Toolkit (MVT)**: Ferramenta de análise de dispositivos móveis.

Com essa API, a detecção de spyware se torna mais acessível, intuitiva e eficiente, permitindo que qualquer pessoa utilize o MVT sem precisar interagir diretamente com o terminal.

## Comece aqui

### **Visão Geral**

A API **Detecção de Spyware** funciona como uma interface entre a GUI e o **MVT (Mobile Verification Toolkit)**, permitindo que os usuários executem análises de dispositivos móveis sem precisar interagir diretamente com o terminal. Para garantir o funcionamento adequado, alguns passos iniciais são necessários.

### **Configuração Inicial**

Antes de utilizar o MVT, é recomendado configurar a **chave da API do VirusTotal**. Essa chave permite realizar consultas e análises detalhadas dos arquivos suspeitos em busca de ameaças.

#### **Definir a chave da API do VirusTotal**

**Endpoint:** `/set-virustotal-api-key`  
**Método:** `POST`

##### **Parâmetro necessário:**

| Nome      | Tipo  | Obrigatório | Descrição                   |
| :-------- | :---: | :---------: | :-------------------------- |
| `api_key` | `str` |     Sim     | Chave da API do VirusTotal. |

##### **Exemplo de requisição:**

```json
{
  "api_key": "SUA_CHAVE_API_AQUI"
}
```

##### **Resposta esperada:**

```json
{
  "success": true,
  "message": "VirusTotal API Key set successfully"
}
```

##### **Possíveis erros:**

- `"Missing required parameter: api_key"` → A chave da API não foi fornecida.
- `"Failed to set API Key."` → Ocorreu um erro ao salvar a chave.

### **Uso da API**

Após configurar a chave da API do VirusTotal, os usuários podem utilizar os demais endpoints para interagir com o MVT. Os comandos funcionam **sem a chave da API**, mas os resultados podem ser **incompletos ou menos precisos**.

#### **Verificar dispositivos conectados via ADB**

**Endpoint:** `/check-adb`  
**Método:** `POST`

##### **Parâmetros:**

| Nome              |  Tipo  | Obrigatório | Descrição                                                               |
| :---------------- | :----: | :---------: | :---------------------------------------------------------------------- |
| `serial`          | `str`  |     Não     | Número de série do dispositivo ou conexão HOST:PORT.                    |
| `iocs_files`      | `list` |     Não     | Lista de arquivos de indicadores de comprometimento (IoCs).             |
| `output_folder`   | `str`  |     Não     | Pasta onde os resultados JSON serão armazenados. (Padrão: `/tmp/adb/`). |
| `fast`            | `bool` |     Não     | Pular verificações demoradas. (Padrão: `False`).                        |
| `list_modules`    | `bool` |     Não     | Lista os módulos disponíveis. (Padrão: `False`).                        |
| `module`          | `str`  |     Não     | Nome de um módulo específico a ser executado.                           |
| `non_interactive` | `bool` |     Não     | Evita perguntas interativas durante o processo. (Padrão: `False`).      |
| `backup_password` | `str`  |     Não     | Senha de backup do Android.                                             |
| `verbose`         | `bool` |     Não     | Ativa o modo detalhado. (Padrão: `False`).                              |

##### **Exemplo de requisição:**

```json
{
  "serial": "emulator-5554",
  "output_folder": "/tmp/adb/",
  "fast": true
}
```

##### **Resposta esperada:**

```json
{
  "success": true,
  "output": [
    {
      "id": 0,
      "status": "INFO",
      "message": "Device analysis completed successfully."
    }
  ]
}
```

##### **Possíveis erros:**

- `"Unsupported content type"` → O formato da requisição não é suportado.
- `"Error executing ADB command"` → O dispositivo pode não estar conectado corretamente.

#### **Verificar e fazer backup do dispositivo**

**Endpoint**: `/check-backup`
**Método**: `POST`

##### **Parâmetros:**

| Nome              |  Tipo  | Obrigatório | Descrição                                                                  |
| :---------------- | :----: | :---------: | :------------------------------------------------------------------------- |
| `backup_path`     | `str`  |     sim     | Local onde será salvo o backup do dispositivo.                             |
| `iocs_files`      | `list` |     Não     | Lista de arquivos de indicadores de comprometimento (IoCs).                |
| `output_folder`   | `str`  |     Não     | Pasta onde os resultados JSON serão armazenados. (Padrão: `/tmp/backup/`). |
| `list_modules`    | `bool` |     Não     | Lista os módulos disponíveis. (Padrão: `False`).                           |
| `non_interactive` | `bool` |     Não     | Evita perguntas interativas durante o processo. (Padrão: `False`).         |
| `backup_password` | `str`  |     Não     | Senha de backup do Android.                                                |
| `verbose`         | `bool` |     Não     | Ativa o modo detalhado. (Padrão: `False`).                                 |

##### **Exemplo de requisição:**

```json
{
  "backup_path": "/tmp/backup.ab",
  "non_interactive": true
}
```

##### **Resposta esperada:**

```json
{
  "success": true,
  "output": [
    {
      "id": 0,
      "status": "INFO",
      "message": "Device analysis completed successfully."
    }
  ]
}
```

##### **Possíveis erros:**

- `"Unsupported content type"` → O formato da requisição não é suportado.

#### **Extrair APKs do dispositivo**

**Endpoint**: `download-apks`
**Método**: `POST`

##### **Parâmetros:**

| Nome            |  Tipo  | Obrigatório | Descrição |
| :-------------- | :----: | :---------: | :-------- |
| `serial`        | `str`  |     Não     |           |
| `all_pks`       | `bool` |     Não     |           |
| `virustotal`    | `bool` |     Não     |           |
| `output_folder` | `str`  |     Não     |           |
| `from_file`     | `str`  |     Não     |           |
| `verbose`       | `bool` |     Não     |           |

###### **Exemplo de requisição:**

```json
{
  "virustotal": true,
  "output_folder": "/tmp/apks/"
}
```

##### **Resposta esperada:**

<!-- Precisa acerta a resposta-->

```json
{
  "success": true,
  "output": [
    {
      "id": 0,
      "status": "INFO",
      "message": "Device analysis completed successfully."
    }
  ]
}
```

##### **Possíveis errors:**

- `"Unsupported content type"` → O formato da requisição não é suportado.

#### **Baixar os IOCs (Indicators of Compromise)**

**Endpoint**: `/download-iocs`
**Method**: `GET`

##### **Resposta esperada:**

##### **Possíveis errors:**

## **Conclusão**

Com essa configuração inicial, a API estará pronta para ser utilizada, permitindo que a GUI envie comandos para o MVT de forma simplificada. Recomenda-se sempre definir a chave da API do VirusTotal para obter resultados mais completos.
