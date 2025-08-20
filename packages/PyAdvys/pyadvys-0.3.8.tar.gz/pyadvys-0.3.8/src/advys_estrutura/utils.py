from pathlib import Path
from advys_estrutura.config import ENCODING


def cria_arquivo_python(arquivo: Path) -> None:
    """
    Cria um novo arquivo e define uma variável `home`.

    Verifica se o arquivo inserido é um arquivo Python(.py) válido!

    Args:
        arquivo (Path): O nome do arquivo a ser criado.

    """

    if arquivo.suffix != ".py":
        raise ValueError(f'Arquivo Python inválido: {arquivo.stem}')

    with open(arquivo, "w", encoding=ENCODING) as arquivo_py:
        arquivo_py.write("from pathlib import Path\n\n")
        arquivo_py.write(f"home = Path.home()\n\n")


def adiciona_linha_ao_arquivo(row, arquivo:Path):
    """
    Adiciona linha ao final de um arquivo.

    Verifica se o arquivo inserido é um arquivo Python(.py) válido!

    Args:
        arquivo (Path): O nome do arquivo a ser criado.

    """


    if arquivo.suffix != ".py":
        raise ValueError(f'Arquivo Python inválido: {arquivo.stem}')


    with open(arquivo, mode="a+", encoding=ENCODING) as arquivo_py:
        arquivo_py.write(f"{row}\n")
