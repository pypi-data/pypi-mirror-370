import argparse
from pathlib import Path

#
from advys_estrutura.utils import cria_arquivo_python, adiciona_linha_ao_arquivo
from advys_estrutura.config import DIR_DESENVOLVIMENTO_REDE, IMAGENS_PY
from advys_configuracoes.config_ini import carrega_configuracao_ini


#
def criar_caminhos_imagem(dir_imagens:Path, arquivo_imagens_py,iniciar=True):
    if iniciar:
        cria_arquivo_python(arquivo_imagens_py)
    for item in dir_imagens.iterdir():
        if item.is_file() and item.suffix == ".png":
            linha = f"{item.stem[4:]} = home / '{item.relative_to(Path.home()).as_posix()}'"
            adiciona_linha_ao_arquivo(linha, arquivo_imagens_py)

        if item.is_dir():
            criar_caminhos_imagem(item, arquivo_imagens_py, iniciar= False)

def executa_atualizacao():
    # Carrega o arquivo de configuração
    config_ini = carrega_configuracao_ini()

    parser = argparse.ArgumentParser(
        description="Gera atualiza o arquivo imagens.py")
    parser.add_argument("-ci", "--caminho_imagens",
                        help="Caminho para pasta de imagens")
    args = parser.parse_args()

    dir_imagens = config_ini["atualiza_imagens"]["caminho_imagens"]
    if args.caminho_imagens:
        dir_imagens = args.caminho_imagens

    Path(dir_imagens).mkdir(parents=True, exist_ok=True)

    criar_caminhos_imagem(Path(dir_imagens), IMAGENS_PY)


if __name__ == "__main__":
    executa_atualizacao()