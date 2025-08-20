import json
from pathlib import Path

#
from advys_configuracoes.constantes import ENCODING
from advys_validadores.arquivo import verifica_arquivo


def escrever_json(dados: dict | list, arquivo: Path):
    if not isinstance(dados, (dict, list)):
        raise ValueError(
            f"Arquivo {arquivo} não criado, dados inválidos."
            f"Tipo recebido: {type(dados).__name__}"
        )

    with open(arquivo, "w", encoding=ENCODING) as arq:
        json.dump(dados, arq, indent=4, ensure_ascii=True)


def ler_json(arquivo) -> dict | list:
    arquivo_json = verifica_arquivo(arquivo).caminho
    with open(arquivo_json, encoding=ENCODING) as arq:
        dados = json.load(arq)
    if not isinstance(dados, (dict | list)):
        raise ValueError(
            f"Arquivo {arquivo} não lido, dados inválidos."
        )
    return dados
