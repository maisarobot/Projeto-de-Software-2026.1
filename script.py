import smtplib
from email.message import EmailMessage
import mimetypes
from dotenv import load_dotenv
import os

load_dotenv()


def enviar_email(destinatario):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA")

    assunto = "Um recado para você!"

    mensagem = """
    Olá, notamos que você não fez login nos últimos 30 dias.
    Volte para o My Bookshelf e atualize suas metas literárias!
    """

    anexo = os.path.join(os.path.dirname(__file__), "email-projeto.png")

    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(mensagem)

    mime_type, _ = mimetypes.guess_type(anexo)

    if mime_type:
        mime_type, mime_subtype = mime_type.split("/")

        with open(anexo, "rb") as arquivo:
            msg.add_attachment(
                arquivo.read(),
                maintype=mime_type,
                subtype=mime_subtype,
                filename=os.path.basename(anexo)
            )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as email:
        email.login(remetente, senha)
        email.send_message(msg)

    print("E-mail enviado com sucesso.")