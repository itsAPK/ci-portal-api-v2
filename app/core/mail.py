from datetime import datetime
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME='plunk',
    MAIL_PASSWORD='sk_279fa345155d1bfcadd52fdf675ad0c8dbfd59b4bfb74e3d',
    MAIL_FROM="support@niranthra.online",
    MAIL_PORT=465,
    MAIL_SERVER='smtp.useplunk.com',
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
