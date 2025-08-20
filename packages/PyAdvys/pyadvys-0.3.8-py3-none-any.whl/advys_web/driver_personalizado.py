
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class NavegadorWeb:
    def __init__(self, lista_opcoes=None):
        opcoes = ChromeOptions()
        if lista_opcoes:
            for opcao in lista_opcoes:
                opcoes.add_argument(opcao)
        opcoes.add_argument("--start-maximized")
        opcoes.add_experimental_option("detach", True)
        self.driver = Chrome(options=opcoes)

    def selenium_chrome_driver(self):
        return self.driver

    def abrir_pagina(self, url):
        self.driver.get(url)

    def encontrar_elemento(self, seletor_css, tempo=10):
        try:
            espera = WebDriverWait(self.driver, tempo)
            elemento = espera.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_css))
            )
        except TimeoutException:
            print(f"Elemento não encontrado no tempo estipulado")
            return None

        return elemento

    def fechar_navegador(self):
        self.driver.quit()
