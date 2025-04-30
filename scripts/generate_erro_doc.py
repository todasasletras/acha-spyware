# generate_error_docs.py

from api.models.types.exception import APIErrorCode
import os

DOCS_PATH = "./documentation/error_codes.md"


def generate_error_code_doc():
    lines = [
        "# 🧾 Tabela de Códigos de Erro da API\n",
        "| Código Numérico | Código | Status HTTP | Mensagem para o Cliente | Descrição Interna |",
        "|:---------------:|:-------|:-----------:|:------------------------|:------------------|",
    ]

    for error in APIErrorCode:
        value = error.value
        lines.append(
            f"| `{value.code}` | `{error.name}` | `{value.status_code}` | "
            f"{value.client_message} | {value.internal_message} |"
        )

    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Documentação gerada em: {os.path.abspath(DOCS_PATH)}")


if __name__ == "__main__":
    generate_error_code_doc()
