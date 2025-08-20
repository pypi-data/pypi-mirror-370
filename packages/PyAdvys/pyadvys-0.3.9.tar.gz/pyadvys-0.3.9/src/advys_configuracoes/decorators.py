from functools import wraps
from advys_configuracoes.config_ini import arquivo_ini, cria_pyadvys_ini

def cria_config_ini(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not arquivo_ini.exists():
            cria_pyadvys_ini()
        return func(*args, **kwargs)
    return wrapper