from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import logging
import smtplib
from pathlib import Path

#
from advys_validadores.emal import Usuario
from advys_validadores.senha import SenhaSimples
from advys_validadores.arquivo import Arquivo


class EmailSmtp:

    def __init__(
        self,
        endereco_email: str,
        senha: str,
        servidor: str = "smtp.gmail.com",
        porta: int = 587
    ):
        """
        Inicializa o objeto EmailSmtp.

        Args:
            endereco_email: Usuario gmail para envio do email via smtp.
            senha: Senha gmail destinada a aplicativos externos.
            servidor: Servidor usado para enviar email, padrão smtp.gmail.com.
            porta: Porta do servidor usada para enviar email, padrão 587.
        """
        self.servidor = servidor
        self.porta = porta
        self.endereco_email = Usuario(email=endereco_email).email
        self.senha = SenhaSimples(valor=senha).valor
        self.email_mime = None

    @property
    def email(self):
        return self.endereco_email

    @property
    def remetente(self):
        return self.endereco_email

    def criar_email_mime(
        self,
        destinatarios: list[str],
        assunto: str,
        mensagem: str,
        copia_para: list[str] = None
    ) -> None:
        """
        Cria o corpo do email (MIME).

        Args:
            destinatarios: Endereços de e-mail dos destinatários.
            assunto: Assunto do email.
            mensagem: Corpo do e-mail em formato HTML.
            copia_para: Endereços de e-mail para enviar uma cópia.

        Raises:
            ValueError: Se a lista de destinatários estiver vazia.
        """
        self.destinatarios = destinatarios
        self.assunto = assunto
        self.copia_para = copia_para or []

        if not destinatarios:
            raise ValueError("Lista de destinatários vazia!")

        # Criação do email (objeto MIMEMultipart)
        email_mime = MIMEMultipart()
        email_mime["From"] = self.remetente
        email_mime["To"] = ", ".join(self.destinatarios)
        email_mime["Subject"] = self.assunto
        if self.copia_para:
            email_mime["Cc"] = ", ".join(self.copia_para)

        # Adiciona a mensagem ao corpo email no formato html
        email_mime.attach(MIMEText(mensagem, "html"))

        #
        self.email_mime = email_mime

    def anexar_arquivo(self, arquivos: list[Path]) -> None:
        """
        Anexa o arquivo ao corpo do email (MIME).

        Args:
            arquivos (list): Arquivos (caminhos) para anexar ao e-mail.

        """

        logging.info("Anexando arquivos")
        for arquivo in arquivos:
            try:
                caminho_arquivo = Arquivo(caminho=arquivo).caminho
                nome_arquivo = caminho_arquivo.name
                with open(caminho_arquivo, "rb") as attachment:
                    part = MIMEApplication(
                        attachment.read(), Name=nome_arquivo
                    )
                    part["Content-Disposition"] = (
                        f'attachment; filename="{nome_arquivo}"'
                    )
                    self.email_mime.attach(part)
                logging.debug(f"{nome_arquivo} - anexado com sucesso")
            except Exception as e:
                logging.error(
                    f"Erro ao anexar arquivo {arquivo.name}: {e}"
                )
        logging.info("Arquivos anexados.")

    def enviar_email(self) -> None:
        """
        Envia o email para todos os destinatários.

        Raises:
            ValueError: Se o email não for criado.
        """
        if not self.email_mime:
            raise ValueError("O e-mail não foi criado!")

        try:
            destinatarios_com_copia = (
                self.destinatarios + self.copia_para
            )

            with smtplib.SMTP(self.servidor, self.porta) as server:
                server.starttls()
                server.login(self.email, self.senha.get_secret_value())
                server.sendmail(
                    self.remetente,
                    destinatarios_com_copia,
                    self.email_mime.as_string()
                )
            logging.info(f'Destinatários:{", ".join(self.destinatarios)}')
            logging.info(f"E-mail enviado com sucesso!")

        except Exception as e:
            logging.error(f"Erro ao enviar email: {e}")
