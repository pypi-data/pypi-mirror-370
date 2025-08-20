import logging
from pathlib import Path
from pydantic import BaseModel, FilePath, ValidationError

class Arquivo(BaseModel):
    caminho: FilePath

def verifica_arquivo(arquivo: Path) -> Arquivo:
    """
    Verifica se o caminho existe e registra o log em caso de erro de validação.
    """
    try:
        return Arquivo(caminho=arquivo)
    except ValidationError as e:
        logging.error(f"Erro no arquivo - {arquivo}: {e}")
        raise
