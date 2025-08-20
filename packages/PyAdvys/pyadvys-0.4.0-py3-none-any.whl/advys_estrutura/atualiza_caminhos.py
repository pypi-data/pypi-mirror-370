import argparse
from pathlib import Path
import re

# módulos instalados
from unidecode import unidecode
from advys_configuracoes.config_ini import carrega_configuracao_ini
from advys_estrutura.config import CAMINHOS_PY
from advys_estrutura.utils import cria_arquivo_python, adiciona_linha_ao_arquivo
from advys_utilitarios.arquivos_json import ler_json


def cria_variavel(prefixo, nome):
    # Validações
    if not isinstance(prefixo, str):
        raise ValueError("O argumento 'prefixo' deve ser uma string.")
    if not isinstance(nome, str):
        raise ValueError("O argumento 'nome' deve ser uma string.")

    nome = re.sub("[.-/\\ ]", "_", nome)
    variavel = unidecode(f"{prefixo[:3]}_" + nome).upper()

    return variavel


def criar_caminhos_estrutura(
    arquivo: Path,
    estrutura: list[dict],
    raiz: Path,
    iniciar: bool = True
):
    if iniciar:
        cria_arquivo_python(arquivo)
    for item in estrutura:
        nome = item["nome"]
        tipo = item["tipo"]
        conteudo = item.get("conteudo")
        caminho = Path(raiz) / f"{nome}"
        if tipo == "diretório" and not caminho.exists():
            caminho.mkdir(exist_ok=True, parents=True)
        var = cria_variavel(tipo, nome)
        linha = (
            f"{var} = home / '{caminho.relative_to(Path.home()).as_posix()}'"
        )
        adiciona_linha_ao_arquivo(linha, arquivo)
        if conteudo:
            criar_caminhos_estrutura(
                arquivo,
                conteudo,
                caminho,
                iniciar=False
            )

def executa_atualizacao():
    # Carrega o arquivo de configuração
    config_ini = carrega_configuracao_ini()

    # Cria parametros
    parser = argparse.ArgumentParser(
        description=(
            "Cria estrutura de diretórios e caminhos Python baseada em "
            "um arquivo JSON."
        )
    )

    # Parâmetro --caminho_estrutura
    parser.add_argument(
        "-ce",
        "--caminho_estrutura",
        help=(
            "Caminho para o arquivo JSON que define a estrutura de "
            "diretórios."
        ),
        type=Path
    )

    # Parâmetro --raiz
    parser.add_argument(
        "-r",
        "--raiz",
        help="Caminho raiz onde a estrutura será criada.",
        type=Path
    )

    # Captura os parametros chamados
    args = parser.parse_args()

    # Pega o caminho raiz definido no arquivo de configuração .ini caso não
    # tenha passado um parâmetro ao executar o script
    raiz = config_ini["atualiza_caminhos"]["raiz"]
    if args.raiz:
        raiz = Path(args.raiz)

    # Pega o caminho da estrutura no arquivo de configuração .ini caso não seja
    # passado nenhum parâmetro ao executar o script
    caminho_estrutura_json = (
        Path(config_ini["atualiza_caminhos"]["caminho_estrutura"])
    )
    if args.caminho_estrutura:
        caminho_estrutura_json = Path(args.caminho_estrutura)

    estrutura = ler_json(caminho_estrutura_json)

    criar_caminhos_estrutura(CAMINHOS_PY, estrutura, raiz, iniciar=True)


if __name__ == "__main__":
    executa_atualizacao()
