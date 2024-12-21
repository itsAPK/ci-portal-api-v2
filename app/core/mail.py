from datetime import datetime
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM="send@imapk.xyz",
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent.parent / "templates",
)


async def send_email(to: list[str], subject: str, context: dict):
    message = MessageSchema(
        subject=subject,
        recipients=to,
        template_body=dict(**context, current_year=datetime.now().year),
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    await fm.send_message(message, template_name="base.html")
