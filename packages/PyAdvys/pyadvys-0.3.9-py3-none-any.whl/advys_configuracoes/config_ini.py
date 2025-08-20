from configparser import ConfigParser
import logging
from pathlib import Path

from advys_configuracoes.constantes import ENCODING, NOME_BIBLIOTECA
from advys_validadores.arquivo import verifica_arquivo

nome_arquivo_ini = "py_advys.ini"
dir_config = Path.home() / f".{NOME_BIBLIOTECA} Config"
arquivo_ini = dir_config / nome_arquivo_ini


def caminho_configuracao_ini():
    return arquivo_ini


def cria_pyadvys_ini(arquivo_config: Path = arquivo_ini):
    """
    Cria um arquivo de configuração .ini padrão para a biblioteca.
    """

    if arquivo_config.exists():
        logging.info(
            f"Arquivo {arquivo_config.name} já existe, pulando a criação..."
        )
        return

    logging.info(f"Criando arquivo {arquivo_config.name}...")

    # Configuração padrão se o ARQUIVO DE CONFIGURAÇÃO não existir
    config = ConfigParser()

    # Configura parâmetros - estrutura/atualiza_estrutura.py
    caminho_estrutura = Path.cwd() / "src" / "estrutura_dir.json"
    raiz = dir_config / "Estrutura"
    raiz.mkdir(parents=True, exist_ok=True)
    config['atualiza_caminhos'] = {
        "caminho_estrutura": str(caminho_estrutura),
        "raiz": str(raiz)
    }

    # Configura parâmetros - estrutura/atualiza_imagens.py
    caminho_imagens = Path.home() / "Imagens Automação Advys"
    caminho_imagens.mkdir(parents=True, exist_ok=True)
    config['atualiza_imagens'] = {
        "caminho_imagens": str(caminho_imagens)
    }

    # Escreve as configurações no arquivo
    with open(arquivo_config, "w", encoding=ENCODING) as a:
        config.write(a)

    logging.info(f"Arquivo {nome_arquivo_ini} criado.")


def carrega_configuracao_ini(arquivo_config: Path = arquivo_ini):
    """
    Carrega o arquivo de configuração .ini
    """

    logging.info(f"Carregando arquivo {arquivo_config.name}")
    arquivo = verifica_arquivo(arquivo_config)
    config = ConfigParser()
    config.read(arquivo.caminho, encoding=ENCODING)
    return config


if __name__ == "__main__":
    py_advys_ini = caminho_configuracao_ini()
    cria_pyadvys_ini()
    verifica_arquivo(py_advys_ini)
