import json
from bson import json_util
import uuid
import base64
from beanie import (
    init_beanie,
)

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

from app.archive.models import Archive
from app.bussiness_unit.models import BussinessUnit
from app.company.models import Company
from app.core.config import settings
from app.division.models import Division
from app.documents.models import Documents
from app.employee.models import Employee
from app.plant.models import Plant
from app.department.models import Department
from app.tools.models import Tools
from app.opportunity.models import (
    ActionPlan,
    ControlBase,
    ControlCost,
    ControlResponse,
    ImprovementBase,
    MeasureAnalysisBase,
    MonthlySavings,
    Opportunity,
    ProjectClosure,
    SSVTool,
    SSVToolBase,
    TeamMember,
    Schedule,
    DefinePhase,
    ControlPhase,
    ImprovementPhase,
    MeasureAnalysisPhase,
)
from app.training.models import Training


async def init_db():
    client = AsyncIOMotorClient('mongodb://mongo:ciportal@116.203.117.55:27012')
    await init_beanie(
        database=client.get_database(settings.MONGODB_DB_NAME),
        document_models=[
            Company,
            Division,
            Plant,
            Department,
            Tools,
            Documents,
            Archive,
            Opportunity,
            Employee,
            ActionPlan,
            TeamMember,
            Schedule,
            DefinePhase,
            ControlPhase,
            ControlCost,
            ControlResponse,
            ControlBase,
            ImprovementBase,
            ImprovementPhase,
            MeasureAnalysisPhase,
            MeasureAnalysisBase,
            SSVTool,
            SSVToolBase,
            BussinessUnit,
            Training,
            ProjectClosure,
            MonthlySavings
        ],
    )


def parse_json(documents):
    return json.loads(json_util.dumps(documents))
