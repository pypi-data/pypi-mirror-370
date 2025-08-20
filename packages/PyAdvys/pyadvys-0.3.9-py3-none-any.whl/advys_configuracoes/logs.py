import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from advys_configuracoes.constantes import ENCODING

def configurar_logging(
    arquivo_log,
    max_bytes=5 * 1024 * 1024,  # 5MB
    backup_count=3,
    habilitar_log_console=False,
    formato_log = '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    nome_log = 'root',
    nivel_log=logging.DEBUG,
):
    caminho = Path(arquivo_log)
    caminho.parent.mkdir(exist_ok=True, parents=True)

    logger = logging.getLogger(nome_log)
    logger.setLevel(nivel_log)

    # Formato do log
    formato = logging.Formatter(formato_log)

    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        arquivo_log, maxBytes=max_bytes, backupCount=backup_count, encoding=ENCODING
    )
    file_handler.setFormatter(formato)

    # Handler opcional para console
    console = None
    if habilitar_log_console:
        console = logging.StreamHandler()
        console.setFormatter(formato)


    # Adiciona os handlers caso não existam
    if not logger.handlers:
        logger.addHandler(file_handler)
        if console:
            logger.addHandler(console)

    return logger