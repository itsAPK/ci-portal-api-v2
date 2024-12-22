from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.databases import init_db
from app.middlewares.telegram_error import TelegramErrorMiddleware
from app.router import router


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa
    # configure_logging()
    await init_db()
    yield


# Common response codes
responses: Set[int] = {
    status.HTTP_400_BAD_REQUEST,
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
    status.HTTP_404_NOT_FOUND,
    status.HTTP_500_INTERNAL_SERVER_ERROR,
}

app = FastAPI( ##
    lifespan=lifespan,
  
)


@app.get("/")
def docs():
    return RedirectResponse("/docs")


# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.USE_CORRELATION_ID:
    from app.middlewares.correlation import CorrelationMiddleware

    app.add_middleware(CorrelationMiddleware)

app.add_middleware(
    TelegramErrorMiddleware,
    telegram_bot_token=settings.TELEGRAM_BOT_TOKEN,
    telegram_chat_id=settings.TELEGRAM_CHAT_ID,
)

app.include_router(router)




