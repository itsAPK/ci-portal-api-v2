import logging
from datetime import datetime
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("email.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME="",
    MAIL_PASSWORD="",
    MAIL_FROM="EPAM@amararaja.com",
    MAIL_PORT=25,
    MAIL_SERVER='10.120.0.104',
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent.parent / "templates",
)


async def send_email(to: list[str], subject: str, context: dict):
    try:
        logger.info(f"Attempting to send email to: {to} | Subject: {subject}")
        logger.debug(f"Email context: {context}")

        message = MessageSchema(
            subject=subject,
            recipients=to,
            template_body=dict(**context, current_year=datetime.now().year),
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="base.html")

        logger.info(f"Email successfully sent to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to} | Error: {e}", exc_info=True)
        return False
