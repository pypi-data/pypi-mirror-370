import pytest
from unittest.mock import patch, MagicMock

from advys_servicos.email_smtp import EmailSmtp

# Configuração inicial para o teste
EMAIL = "teste@gmail.com"
SENHA = "senha123"
DESTINATARIO = ["destinatario@gmail.com"]
ASSUNTO = "Teste"
MENSAGEM = "<p>Mensagem de teste</p>"



@pytest.fixture
def email_smtp():
    return EmailSmtp(endereco_email=EMAIL, senha=SENHA)

def test_criar_email_mime(email_smtp):
    email_smtp.criar_email_mime(
        destinatarios=DESTINATARIO,
        assunto=ASSUNTO,
        mensagem=MENSAGEM
    )
    assert email_smtp.email_mime is not None
    assert email_smtp.email_mime["Subject"] == ASSUNTO

@patch("advys_servicos.email_smtp.smtplib.SMTP")
def test_enviar_email(mock_smtp, email_smtp):
    email_smtp.criar_email_mime(
        destinatarios=DESTINATARIO,
        assunto=ASSUNTO,
        mensagem=MENSAGEM
    )

    # Rodar o método de envio
    email_smtp.enviar_email()

    # Verificar se a conexão SMTP foi aberta
    mock_smtp.assert_called_with(email_smtp.servidor, email_smtp.porta)

    # Verificar se o login foi chamado
    instance = mock_smtp.return_value.__enter__.return_value
    instance.login.assert_called_with(
        email_smtp.email,
        email_smtp.senha.get_secret_value()
    )

    # Verificar se o e-mail foi enviado
    instance.sendmail.assert_called()

@patch("advys_servicos.email_smtp.open", create=True)
def test_anexar_arquivo(mock_open, email_smtp, tmp_path):
    # Simular arquivo temporário
    fake_file = tmp_path / "teste.txt"
    fake_file.write_text("conteudo do arquivo")

    # Criar o e-mail primeiro
    email_smtp.criar_email_mime(
        destinatarios=DESTINATARIO,
        assunto=ASSUNTO,
        mensagem=MENSAGEM
    )

    # Mock do open
    mock_open.return_value.__enter__.return_value.read.return_value = b"conteudo do arquivo"

    # Executa anexar
    email_smtp.anexar_arquivo([fake_file])

    # Verifica se open foi chamado
    mock_open.assert_called_with(fake_file, "rb")