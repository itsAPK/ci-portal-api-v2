from datetime import datetime
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME='MS_TG8oUk@niranthra.online',
    MAIL_PASSWORD='q1sosCjeWQAuLUAR',
    MAIL_FROM="MS_TG8oUk@niranthra.online",
    MAIL_PORT=587,
    MAIL_SERVER='smtp.mailersend.net',
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent.parent / "templates",
)


async def send_email(to: list[str], subject: str, context: dict):
    try:
        print(context)
        message = MessageSchema(
            subject=subject,
            recipients=to,
            template_body=dict(**context, current_year=datetime.now().year),
            subtype=MessageType.html,
        )

        fm = FastMail(conf)

        await fm.send_message(message, template_name="base.html")
    except Exception as e:
        print(e)
        return False
