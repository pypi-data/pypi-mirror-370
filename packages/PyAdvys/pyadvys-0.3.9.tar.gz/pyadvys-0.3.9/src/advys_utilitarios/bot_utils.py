from random import randint

from botcity.core import DesktopBot
from loguru import logger
from mousekey import MouseKey


class BotUtils:
    def __init__(self, bot=None, mouse=None):
        self.bot = bot or DesktopBot()
        self.mouse = mouse or MouseKey()
        self.mouse.enable_failsafekill("ctrl+e")

    def localizar_img(self, label, tempo_busca=10000, local_exato=False):
        img = self.bot.find(label=label, waiting_time=tempo_busca)
        if not img:
            logger.error(f"Erro buscando {label}")
            return None

        centro_x = (img.width // 2) + img.left
        centro_y = (img.height // 2) + img.top

        if local_exato:
            return (centro_x, centro_y)
        else:
            x_aleatorio = centro_x + randint(-3, 3)
            y_aleatorio = centro_y + randint(-3, 3)
            return (x_aleatorio, y_aleatorio)

    def clicar(
        self,
        label: str,
        tempo_busca=10000,
        duplo=False,
        natural=True,
        relativo: tuple = None,
    ):
        centro_x, centro_y = self.localizar_img(label, tempo_busca)

        if relativo:
            x_rel, y_rel = relativo
            self.mouse.move_to_natural(centro_x, centro_y)
            self.mouse.left_click_xy_natural_relative(x_rel, y_rel)
        elif natural:
            self.mouse.left_click_xy_natural(centro_x, centro_y)
        else:
            self.mouse.left_click_xy(centro_x, centro_y)

        if duplo:
            self.mouse.left_click_xy(centro_x, centro_y)

        return centro_x, centro_y

    def digitar(self, texto, enter=False):
        self.bot.kb_type(texto)
        logger.info(f"Texto digitado: {texto}")
        if enter:
            self.bot.enter()

    def pressionar(self, telcas: list):
        self.bot.key_press(telcas)
        logger.info(f"Teclas pressionadas: {telcas}")
