from pydantic import ValidationError
import pytest

from advys_validadores.emal import *

def test_email_valido():
    usuario = Usuario(email="teste@teste.com")
    assert usuario.email == "teste@teste.com"

def test_email_sem_arroba():
    with pytest.raises(ValidationError):
        Usuario(email="testeteste.com")

def test_email_vazio():
    with pytest.raises(ValidationError):
        Usuario(email="")

def test_email_sem_dominio():
    with pytest.raises(ValidationError):
        Usuario(email="teste@")