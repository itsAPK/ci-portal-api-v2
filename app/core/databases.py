import json
from bson import json_util
import uuid
import base64
from beanie import (
    init_beanie,
)

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.company.models import Company
from app.core.config import settings
from app.division.models import Division
from app.plant.models import Plant
from app.department.models import Department


async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=client.get_database(settings.MONGODB_DB_NAME),
        document_models=[Company, Division, Plant, Department],
    )
