from advys_estrutura import imagem
from advys_utilitarios.funcoes_pyautogui import busca_img,clica_na_imagem
from advys_web.driver_personalizado import NavegadorWeb
import pyautogui as pyg

def login_dominio_web(
    email_dominio_web: str,
    senha_dominio_web: str,
    usuario_plugin: str,
    senha_plugin: str,
    programa: str = "folha"
) -> None:
    """
    Loga no Domínio Web.

    Precisa ter o plugin instalado.

    Args:
        email_dominio_web (str): Email usado para logar na primeira
            etapa de login do Domínio Web.
        senha_dominio_web (str): Senha usada para logar na primeira
            etapa de login do Domínio Web.
        usuario_plugin (str): Usuário usado para logar no plugin do
            Domínio Web.
        senha_plugin (str): Senha usada para logar no plugin do
            Domínio Web.
    """

    # cria uma instancia do driver personalizado NavegadorWeb
    driver = NavegadorWeb()
    driver.abrir_pagina(url="https://www.dominioweb.com.br/")

    # clica no botão entrar
    btn_entrar_1 = driver.encontrar_elemento("#enterButton")
    btn_entrar_1.click()

    # insere o email
    caixa_email = driver.encontrar_elemento("#username")
    caixa_email.send_keys(email_dominio_web)

    # clica no botão entrar
    pyg.press("tab")
    pyg.press("enter")

    # insere a senha
    caixa_senha = driver.encontrar_elemento("#password")
    caixa_senha.send_keys(senha_dominio_web)

    # clica no botão entrar
    pyg.press("tab", presses=3)
    pyg.press("enter")


    # abre o plugin do dominio web
    while True:
        permitir_plugin = busca_img(imagem.permitir_plugin)
        permitir_plugin_en = busca_img(imagem.permitir_plugin_en)
        if permitir_plugin or permitir_plugin_en:
            pyg.hotkey("shift", "tab")
            pyg.press("enter")
            break

        pyg.sleep(1)

    # verifica se a janela com a lista de programas está aberta
    while not busca_img(imagem.dominio_web_lista_programas):
        pyg.sleep(1)
        pass

    # clica no icone do programa informado
    if programa == "folha":
        clica_na_imagem(imagem.icone_folha, double=True)
    elif programa == "escrita fiscal":
        clica_na_imagem(imagem.icone_escrita_fiscal, double=True)

    # faz login no plugin do dominio web
    while True:
        if busca_img(imagem.login_fiscal):
            pyg.write(usuario_plugin)
            pyg.press('tab')
            pyg.write(senha_plugin)
            pyg.press('enter')

        if busca_img(imagem.logo_dominio):
            break

    # espera o logo desaparecer
    while True:
        if not busca_img(imagem.logo_folha):
            break
        pyg.sleep(1)

    driver.fechar_navegador()
