from pathlib import Path

#
import pyautogui as pyg


def busca_img(
    imagem: Path, busca: str = "rapida", confiabilidade: float = 0.9
) -> tuple[int, int] | None:
    """
    Usa o pyautogui para retornar as coordenadas x, y da imagem.

    Args:
        imagem (Path): caminho da imagem.
        busca (str): tipo de busca ('lenta', 'normal', 'rapida').
        confiabilidade (float): nível de precisão da imagem.

    Returns:
        tupla ou None: retorna as coordenadas (x, y) em uma tupla ou
            None se não encontrar.

    Exemplo:
        cordenadas = busca_img("caminho/completo/imagem.png",
            busca="rapida")
    """


    tipos_de_busca = {
        "lenta": (1200, 0.5),
        "normal": (120, 0.5),
        "rapida": (1, 0.5),
    }

    # Verifica se o valor para busca está correto
    if busca not in tipos_de_busca:
        raise ValueError(
            f"Valor de busca inválido. Opções: {list(tipos_de_busca.keys())}"
        )

    #
    tentativas, atraso = tipos_de_busca[busca]

    for tentativa in range(tentativas):
        try:
            pyg.sleep(atraso)
            cordenadas = pyg.locateCenterOnScreen(
                str(imagem), grayscale=True, confidence=confiabilidade
            )

            # Caso ache as cordenadas da imagem
            if cordenadas:
                if tentativa > 0:
                    print(
                        f"Imagem {imagem.name} encontrada após\
                        {tentativa + 1} tentativas."
                    )
                return cordenadas


        except pyg.ImageNotFoundException:
            continue


        except Exception as e:
            print(f"Erro durante a busca da imagem: {e}")
            raise

    if busca != "rapida":
        print("Imagem não encontrada após o número máximo de tentativas")
    return None


def clica_na_imagem(
    imagem: Path,
    busca: str = "normal",
    double: bool = False,
    duracao: float = 0.5
) -> None:
    """
    Clica nas cordenadas da imagem informada.

    Args:
        imagem (Path): caminho da imagem.
        busca (str): tipo de busca ('lenta', 'normal', 'rapida').
        double (bool): define o click duplo.
        duracao (float): temo que o cursor levará para se mover até as
            cordenadas da imagem.
    """
    coordenadas = busca_img(imagem, busca=busca)
    try:
        if double:
            pyg.doubleClick(coordenadas)
        else:
            pyg.click(coordenadas, duration=duracao)
        print(f"Imagem {imagem.name} clicada")
    except Exception as e:
        print(f"Erro ao tentar clicar na imagem: {e}")
