import importlib.metadata

# Constantes
ENCODING = "utf-8"
NOME_BIBLIOTECA = "PyAdvys"

def get_versao():
    return importlib.metadata.version(NOME_BIBLIOTECA)

VERSAO = get_versao()
