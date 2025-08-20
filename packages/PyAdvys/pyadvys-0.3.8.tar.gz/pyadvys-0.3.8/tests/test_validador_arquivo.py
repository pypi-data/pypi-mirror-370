from pathlib import Path
from pydantic import ValidationError
import pytest

from advys_validadores.arquivo import Arquivo


def test_caminho_valido():
    with pytest.raises(ValidationError):
        Arquivo(caminho=Path(__file__).parent)

def test_caminho_string():
    with pytest.raises(ValidationError):
        Arquivo(caminho="caminho/inválido")
