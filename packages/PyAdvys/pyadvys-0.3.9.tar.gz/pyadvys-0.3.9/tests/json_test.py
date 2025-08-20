import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from advys_utilitarios.arquivos_json import escrever_json, ler_json  # ajuste para o nome do seu módulo

# Cria um diretório temporário para os testes
@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

def test_escrever_json_dict(temp_dir):
    caminho = temp_dir / "arquivo.json"
    dados = {"chave": "valor"}

    escrever_json(dados, caminho)

    with open(caminho, encoding="utf-8") as f:
        conteudo = json.load(f)

    assert conteudo == dados

def test_escrever_json_lista(temp_dir):
    caminho = temp_dir / "arquivo.json"
    dados = [1, 2, 3]

    escrever_json(dados, caminho)

    with open(caminho, encoding="utf-8") as f:
        conteudo = json.load(f)

    assert conteudo == dados

def test_escrever_json_dados_invalidos(temp_dir):
    caminho = temp_dir / "arquivo.json"
    dados = "string inválida"

    with pytest.raises(ValueError, match="dados inválidos"):
        escrever_json(dados, caminho)

def test_ler_json_dict(temp_dir):
    caminho = temp_dir / "arquivo.json"
    dados = {"chave": "valor"}

    caminho.write_text(json.dumps(dados), encoding="utf-8")

    resultado = ler_json(caminho)

    assert resultado == dados

def test_ler_json_lista(temp_dir):
    caminho = temp_dir / "arquivo.json"
    dados = [1, 2, 3]

    caminho.write_text(json.dumps(dados), encoding="utf-8")

    resultado = ler_json(caminho)

    assert resultado == dados

def test_ler_json_malformado(temp_dir):
    caminho = temp_dir / "arquivo.json"
    caminho.write_text("{chave sem aspas: valor}", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        ler_json(caminho)

def test_ler_json_dados_invalidos(temp_dir):
    caminho = temp_dir / "arquivo.json"
    caminho.write_text('"string inválida"', encoding="utf-8")

    with pytest.raises(ValueError, match="dados inválidos"):
        ler_json(caminho)
