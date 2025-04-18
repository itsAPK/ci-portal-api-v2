from datetime import datetime
import json
import os
import shutil
import traceback
from typing import Optional
from beanie import PydanticObjectId
from fastapi import BackgroundTasks, File, HTTPException, UploadFile, status
from app.core.databases import parse_json
from app.core.mail import send_email
from app.employee.models import Employee
from app.opportunity.models import (
    ActionPlan,
    ActionPlanRequest,
    ActionPlanUpdate,
    ControlBase,
    ControlPhase,
    ControlRequest,
    ControlUpdate,
    DefinePhase,
    DefinePhaseRequest,
    DefinePhaseUpdate,
    ImprovementBase,
    ImprovementPhase,
    ImprovementRequest,
    ImprovementUpdate,
    MeasureAnalysisBase,
    MeasureAnalysisPhase,
    MeasureAnalysisRequest,
    MonthlySavings,
    MonthlySavingsRequest,
    MonthlySavingsUpdate,
    Opportunity,
    OpportunityRequest,
    OpportunityUpdate,
    ProjectClosure,
    ProjectClosureRequest,
    ProjectClosureUpdate,
    SSVTool,
    SSVToolBase,
    SSVToolRequest,
    Schedule,
    ScheduleRequest,
    ScheduleUpdate,
    Status,
    TeamMember,
    TeamMemberRequest,
)
from app.plant.models import Plant
from app.schemas.api import ResponseStatus
from beanie.operators import ElemMatch

from bson import ObjectId, json_util

from app.utils import get_initials
from app.utils.upload import save_file
from app.core.config import settings


DEPARTMENT_KPI_PATH = "uploads/define-phase/department-kpi"
LAST_SIX_TREND_PATH = "uploads/define-phase/last-six-trend"
ISO_PLOT_PATH = "uploads/define-phase/iso-plot"
CONCENTRATION_CHART_PATH = "uploads/define-phase/concentration-chart"
PROCESS_FLOW_DIAGRAM_PATH = "uploads/define-phase/process-flow-diagram"
P_CHART = "uploads/define-phase/p-chart"
SSV_TOOL_PATH = "uploads/ssv-tool"
MEASURE_ANALYSIS_PATH = "uploads/measure-analysis"
IMPROVEMENT_PATH = "uploads/improvement"
CONTROL_PATH = "uploads/control"
PROJECT_CLOSURE_PATH = "uploads/project-closure"
OPPORTUNITY_CATEGORY_PATH = "uploads/opportunity-category"
ABNORMALITIES_PATH = "uploads/define-phase/abnormalities"
TOOL_CONDITIONS_PATH = "uploads/define-phase/tool-conditions"


class OppurtunityService:
    def __init__(self):
        pass

    async def create(
    self,
    data: OpportunityRequest,
    created_by: Employee,
    background_tasks: BackgroundTasks,
):
        values = data.model_dump().copy()  # Create a copy to avoid mutation issues

        # Fetch plant
        plant = await Plant.get(values["plant"])
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Plant not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
            
        print(values['plant'], values["category"])
        
        pipeline = [
            {
                "$match": {
                    "plant.name": plant.model_dump()['name'], 
                    "category": values["category"],  
                    "opportunity_year": f"{datetime.now().year}-{datetime.now().year + 1}",  
                }
            },
           
        ]

        count = await self.query_count(pipeline)

        opportunity_id = f"{plant.name.strip()}/{get_initials(values['category'])}/{datetime.now().year}-{datetime.now().year + 1}/{str(count + 1).zfill(3)}"

        values.pop("plant")

        created_by = await Employee.get(created_by) if isinstance(created_by, ObjectId) else created_by

        opportunity = Opportunity(
            **values,
            opportunity_id=opportunity_id,
            created_by=created_by,
            plant=plant,
            status=(
                Status.OPEN_FOR_ASSIGNING
                if values["category"] == "Black Belt"
                else Status.OPPORTUNITY_COMPLETED
            ),
        )

        await opportunity.insert()

        return opportunity


    async def assign_project_leader(
        self,
        opportunity_id: PydanticObjectId,
        employee_id: PydanticObjectId,
        background_tasks: BackgroundTasks,
    ):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        employee = await Employee.get(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        await opportunity.set(
            {
                "project_leader": employee,
                "status": (
                    Status.PROJECT_ASSIGNED
                    if opportunity.category == "Black Belt"
                    else Status.OPPORTUNITY_COMPLETED
                ),
            }
        )
        print(opportunity)

        await opportunity.save()
        
        if opportunity.category == "Black Belt":
            a = background_tasks.add_task(
                send_email,
                [opportunity.project_leader.email],
                "CIRTS Portal: New Opportunity Assigned ",
                {
                    "user": f"{employee.name}",
                    "message": (
                        f"<p>You have been assigned to Opportunity <strong>{opportunity.opportunity_id}</strong>.</p>"
                        f"<p>Please take a moment to review the details and start by updating the savings type and estimated savings.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )
            
          
            
            admins = await Employee.find(Employee.role == "admin").to_list()
            print(admins)
            for admin in admins:
                background_tasks.add_task(
                send_email,
                [admin.email],
                f"CIRTS Portal: Opportunity ({opportunity.opportunity_id}) Assigned",
                {
                    "user": f"{admin.name}",
                    "message": (
                        f"<p>Opportunity <strong>{opportunity.opportunity_id}</strong> assigned to {employee.name} ({employee.designation} - {employee.department}).</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )
            
            
        return opportunity

    async def get(self, opportunity_id: PydanticObjectId):
        opportunity = await Opportunity.get(opportunity_id)
        print(opportunity)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        return opportunity

    async def get_all(self, page: int, page_size: int):
        skip = (page - 1) * page_size
        total_items = await self.count()
        results = await Opportunity.find().skip(skip).limit(page_size).to_list()
        total_pages = (total_items + page_size - 1) // page_size
        remaining_items = max(0, total_items - (skip + len(results)))
        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "data": results,
            "remaining_items": remaining_items,
        }

    async def count(self):
        return await Opportunity.find().count()

    async def query(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count(query)
        results = await Opportunity.aggregate(
            query + [{"$skip": skip}, {"$limit": page_size}]
        ).to_list()
        total_pages = (total_items + page_size - 1) // page_size
        remaining_items = max(0, total_items - (skip + len(results)))
        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "data": parse_json(results),
            "remaining_items": remaining_items,
        }

    async def query_count(self, filter):
        results = await Opportunity.aggregate(filter).to_list()
        return len(results)

    async def export_query(self, filter: list[dict]):
        print(filter)
        query = [] + filter
        total_items = await self.query_count(query)
        results = await Opportunity.aggregate(query).to_list()
        print(results)
        return {
            "total_items": total_items,
            "data": parse_json(results),
        }
    
    async def get_count_by_status(self):
        pipeline = [
    {"$match": {"category": "Black Belt"}},
        {
            "$addFields": {
                "phase": {
                    "$switch": {
                        "branches": [
                            # {
                            #     "case": {"$eq": ["$status", "Open for Assigning"]},
                            #     "then": "pending"
                            # },
                            # {
                            #     "case": {"$in": ["$status", ["Project Assigned", "Details Updated"]]},
                            #     "then": "started"
                            # },
                            {
                                "case": {"$in": ["$status", ["Define Phase Completed", "SSV's Tools Updated", "Measure & Analyze Phase Pending"]]},
                                "then": "define"
                            },
                            {
                                "case": {"$in": ["$status", ["Measure & Analyze Phase Completed", "Improvement Phase Pending"]]},
                                "then": "measure_analysis"
                            },
                            {
                                "case": {"$in": ["$status", ["Improvement Phase Completed", "Control Phase Pending"]]},
                                "then": "improvement"
                            },
                            {
                                "case": {"$in": ["$status", [
                                    "Control Phase Completed",
                                    "Project Closure Pending (CIHead)",
                                    "Project Closure Pending (HOD)",
                                    "Project Closure Pending (LOF)",
                                    "Project Closure Pending (Costing Head)"
                                ]]},
                                "then": "control"
                            },
                            {
                                "case": {"$in": ["$status", [
                                    "Project Completed",
                                    "Opportunity Completed"
                                ]]},
                                "then": "project_completed"
                            }
                        ],
                        "default": "unknown"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$phase",
                "count": {"$sum": 1}
            }
        }
    ]


        results = await Opportunity.aggregate(pipeline).to_list()
        data = parse_json(results)

        phase_counts = {

            "define": 0,
            "measure_analysis": 0,
            "improvement": 0,
            "control": 0,
            "project_completed": 0
        }

        for item in data:
            phase = item["_id"]
            if phase in phase_counts:
                phase_counts[phase] = item["count"]

        return phase_counts

    async def delete(self, id: PydanticObjectId):
        print(id)
        opportunity = await Opportunity.get(id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        await opportunity.delete()
        return opportunity
    
    async def upload_a3(self, id: PydanticObjectId, file: str):
        opportunity = await Opportunity.get(id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        
        opportunity.a3_file = file
        await opportunity.save()
        return opportunity

    async def update(self, data: OpportunityUpdate, id: PydanticObjectId,employee_id :str,background_tasks : BackgroundTasks):
        values = data.model_dump(exclude_none=True)
        opportunity = await Opportunity.get(id)
        
        if opportunity.project_leader != None and employee_id == opportunity.project_leader.employee_id:
            admins = await Employee.find(Employee.role == "admin").to_list()
            for admin in admins:
                background_tasks.add_task(
                send_email,
                [admin.email],
                f"CIRTS Portal: Opportunity ({opportunity.opportunity_id}) is updated",
                {
                    "user": f"{admin.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been updated by Project Leader {opportunity.project_leader.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )

        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        if data.plant:
            plant = await Plant.get(values["plant"])

            values.pop("plant")
            opportunity.plant = plant
        for key, value in values.items():
            if value is not None and hasattr(opportunity, key):
                setattr(opportunity, key, value)

        await opportunity.save()
        return opportunity

    async def upload_files_to_opportunity(self, opportunity_id: PydanticObjectId, files: list[str]):
        try:
            print(f"Opportunity ID: {opportunity_id}, Files: {files}")

            # Fetch the opportunity
            opportunity = await Opportunity.get(opportunity_id)
            if not opportunity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Opportunity not found",
                        "success": False,
                        "status": ResponseStatus.DATA_NOT_FOUND.value,
                        "data": None,
                    },
                )

            if opportunity.file is None:
                opportunity.file = []

            print(f"Existing Files: {opportunity.file}")

            for file in files:
                opportunity.file.append(file)

            await opportunity.save()

            print(f"Updated Files: {opportunity.file}")

            return opportunity

        except Exception as e:
            print("Error occurred:", str(e))
            traceback.print_exc()  # Print full stack trace for debugging
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def approve(
        self,
        id: PydanticObjectId,
        user_id: PydanticObjectId,
        role: str,
        background_tasks: BackgroundTasks,
    ):
        opportunity = await Opportunity.get(id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        head = await Employee.get(user_id)

        if not head:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "head not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        if role == "ci_head":
            if head.role != "ci_head":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Role is not ci head",
                        "success": False,
                        "status": ResponseStatus.DATA_NOT_FOUND.value,
                        "data": None,
                    },
                )

            opportunity.is_approved_by_ci_head = True
            opportunity.status = Status.PROJECT_CLOSURE_PENDING_HOD

            background_tasks.add_task(
                send_email,
                [opportunity.plant.hod.email],
                f"CIRTS Portal : Approval Requested For Opportunity {opportunity.opportunity_id} (CIRTS Portal) ",
                {
                    "user": f"{opportunity.plant.hod.name}",
                    "message": (
                        f"<p>The project closure has been submitted for Opportunity <strong>{opportunity.opportunity_id}</strong> by <strong>{opportunity.project_leader.name}</strong> "
                        f"({opportunity.project_leader.designation}).</p>"
                        f"<p>We kindly ask you to take a moment to review the details and approve the opportunity at your earliest convenience.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )

            background_tasks.add_task(
                send_email,
                [opportunity.project_leader.email],
                f"CIRTS Portal : Opportunity ( {opportunity.opportunity_id} ) Approved",
                {
                    "user": f"{opportunity.project_leader.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by CI Head {opportunity.plant.ci_head.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            ),
            
            
            admins = await Employee.find_all(Employee.role == "admin")
            for admin in admins:
                background_tasks.add_task(
                send_email,
                [admin.email],
                f"CIRTS Portal: Opportunity ({opportunity.opportunity_id}) Approved By CI Head",
                {
                    "user": f"{admin.name}",
                    "message": (
                         f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by CI Head {opportunity.plant.ci_head.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )

        elif role == "hod":
            if head.role != "hod":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Role is not hod",
                        "success": False,
                        "status": ResponseStatus.DATA_NOT_FOUND.value,
                        "data": None,
                    },
                )

            opportunity.is_approved_by_hod = True
            opportunity.status = Status.PROJECT_CLOSURE_PENDING_LOF

            background_tasks.add_task(
                send_email,
                [opportunity.plant.lof.email],
                f"CIRTS Portal : Approval Requested For Opportunity {opportunity.opportunity_id} ",
                {
                    "user": f"{opportunity.plant.lof.name}",
                    "message": (
                        f"<p>The project closure has been submitted for Opportunity <strong>{opportunity.opportunity_id}</strong> by <strong>{opportunity.project_leader.name}</strong> "
                        f"({opportunity.project_leader.designation}).</p>"
                        f"<p>We kindly ask you to take a moment to review the details and approve the opportunity at your earliest convenience.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )
            
            
            admins = await Employee.find_all(Employee.role == "admin")
            for admin in admins:
                background_tasks.add_task(
                send_email,
                [admin.email],
                f"CIRTS Portal: Opportunity ({opportunity.opportunity_id}) Approved By HOD",
                {
                    "user": f"{admin.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by HOD {opportunity.plant.hod.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )

            background_tasks.add_task(
                send_email,
                [opportunity.project_leader.email],
                f"CIRTS Portal : Opportunity ( {opportunity.opportunity_id} ) Approved",
                {
                    "user": f"{opportunity.project_leader.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by HOD {opportunity.plant.hod.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            ),

        elif role == "lof":
            if head.role != "lof":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Role is not lof",
                        "success": False,
                        "status": ResponseStatus.DATA_NOT_FOUND.value,
                        "data": None,
                    },
                )

            opportunity.is_approved_by_lof = True
            opportunity.status = Status.PROJECT_CLOSURE_PENDING_COSTING_HEAD

            background_tasks.add_task(
                send_email,
                [opportunity.plant.cs_head.email],
                f"CIRTS Portal : Approval Requested For Opportunity {opportunity.opportunity_id} (CIRTS Portal) ",
                {
                    "user": f"{opportunity.plant.cs_head.name}",
                    "message": (
                        f"<p>The project closure has been submitted for Opportunity <strong>{opportunity.opportunity_id}</strong> by <strong>{opportunity.project_leader.name}</strong> "
                        f"({opportunity.project_leader.designation}).</p>"
                        f"<p>We kindly ask you to take a moment to review the details and approve the opportunity at your earliest convenience.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )

            background_tasks.add_task(
                send_email,
                [opportunity.project_leader.email],
                f"CIRTS Portal : Opportunity ( {opportunity.opportunity_id} ) Approved",
                {
                    "user": f"{opportunity.project_leader.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by LOF {opportunity.plant.lof.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            ),
            
            admins = await Employee.find_all(Employee.role == "admin")
            for admin in admins:
                background_tasks.add_task(
                send_email,
                [admin.email],
                f"CIRTS Portal: Opportunity ({opportunity.opportunity_id}) Approved By LOF",
                {
                    "user": f"{admin.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by LOF {opportunity.plant.lof.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )

        elif role == "cs_head":
            if head.role != "cs_head":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Role is not cs head",
                        "success": False,
                        "status": ResponseStatus.DATA_NOT_FOUND.value,
                        "data": None,
                    },
                )

            opportunity.is_approved_by_cs_head = True
            opportunity.status = Status.OPPORTUNITY_COMPLETED
            background_tasks.add_task(
                send_email,
                [opportunity.project_leader.email],
                f"CIRTS Portal : Opportunity ( {opportunity.opportunity_id} ) Approved",
                {
                    "user": f"{opportunity.project_leader.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by CS Head {opportunity.plant.cs_head.name}.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )
            background_tasks.add_task(
                send_email,
                [opportunity.project_leader.email],
                f"CIRTS Portal : Opportunity ( {opportunity.opportunity_id} ) Completed",
                {
                    "user": f"{opportunity.project_leader.name}",
                    "message": (
                        f"<p>Opportunity <strong>{opportunity.opportunity_id}</strong> has been successfully completed in the CIRTS Portal.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            ),
            
            
            admins = await Employee.find_all(Employee.role == "admin")
            for admin in admins:
                background_tasks.add_task(
                send_email,
                [admin.email],
                f"CIRTS Portal: Opportunity ({opportunity.opportunity_id}) Approved By CS Head & Compelted",
                {
                    "user": f"{admin.name}",
                    "message": (
                        f"Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by CS Head {opportunity.plant.cs_head.name} and successfully completed .</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )

        await opportunity.save()
        return opportunity


class ActionPlanService:
    def __init__(self):
        pass

    async def create(self, data: ActionPlanRequest, opportunity_id: PydanticObjectId):
        values = data.model_dump()
        opportunity = await Opportunity.get(opportunity_id)
        print(opportunity)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        action_plan = ActionPlan(**values, opportunity_id=opportunity_id)
        opportunity.action_plan.append(action_plan)
        await opportunity.save()
        return action_plan

    async def get(self, action_plan_id: PydanticObjectId):
        print(action_plan_id)
        action_plan = await Opportunity.aggregate(
            [
                {"$unwind": "$action_plan"},
                {"$match": {"action_plan._id": ObjectId(action_plan_id)}},
                {"$replaceRoot": {"newRoot": "$action_plan"}},
            ]
        ).to_list()

        print(action_plan)
        if not action_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "action plan not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        res = parse_json(action_plan)
        print(res)
        return res[0]

    async def update(self, data: ActionPlanUpdate, action_plan_id: PydanticObjectId):
        updated_values = data.model_dump(exclude_none=True)
        print("Updated Values:", updated_values)

        opportunity = await Opportunity.find_one(
            ElemMatch(
                Opportunity.action_plan, ActionPlan.id == ObjectId(action_plan_id)
            )
        )

        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        print("Opportunity:", opportunity)

        for index, action_plan in enumerate(opportunity.action_plan):
            print("Checking Action Plan:", action_plan)
            if str(action_plan.id) == str(action_plan_id):
                print("Found Matching Action Plan ID:", action_plan.id)

                for key, value in updated_values.items():
                    if hasattr(action_plan, key):
                        setattr(action_plan, key, value)

                opportunity.action_plan[index] = action_plan
                break
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "action plan not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.save()
        return opportunity.action_plan[index]

    async def delete(self, action_plan_id: PydanticObjectId):
        res = await Opportunity.find_one(
            ElemMatch(
                Opportunity.action_plan, ActionPlan.id == ObjectId(action_plan_id)
            )
        )
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "action plan not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [
            action_plan
            for action_plan in res.action_plan
            if action_plan.id != action_plan_id
        ]
        res.action_plan = data
        await res.save()
        return True


class ProjectScheduleService:
    def __init__(self):
        pass

    async def create(self, data: ScheduleRequest, opportunity_id: PydanticObjectId):
        values = data.model_dump()
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        schedule = Schedule(**values, opportunity_id=opportunity_id)
        opportunity.schedules.append(schedule)
        await opportunity.save()
        return schedule

    async def get(self, schedule_id: PydanticObjectId):
        schedule = await Opportunity.aggregate(
            [
                {"$unwind": "$schedules"},
                {"$match": {"schedules._id": ObjectId(schedule_id)}},
                {"$replaceRoot": {"newRoot": "$schedules"}},
            ]
        ).to_list()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "schedule not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        res = parse_json(schedule)
        return res[0]

    async def update(self, data: ScheduleUpdate, schedule_id: PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        data = await Opportunity.find_one(
            ElemMatch(Opportunity.schedules, Schedule.id == ObjectId(schedule_id))
        )
        schedule = None
        for res in data.schedules:
            if str(res.id) == schedule_id:

                for key, value in values.items():
                    if value is not None and hasattr(res, key):
                        setattr(res, key, value)
                schedule = res

        await data.save()
        return schedule

    async def delete(self, schedule_id: PydanticObjectId):
        res = await Opportunity.find_one(
            ElemMatch(Opportunity.schedules, Schedule.id == ObjectId(schedule_id))
        )
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "schedule not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [schedule for schedule in res.schedules if schedule.id != schedule_id]
        res.schedules = data
        await res.save()


class TeamMemberService:
    def __init__(self):
        pass

    async def create(
        self,
        data: TeamMemberRequest,
        opportunity_id: PydanticObjectId,
        background_tasks: BackgroundTasks,
    ):
        values = data.model_dump()
        employee = await Employee.get(values["employee_id"])
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        opportunity = await Opportunity.find_one(Opportunity.id == opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        values.pop("employee_id")
        team_member = TeamMember(**values, employee=employee)

        opportunity.team_members.append(team_member)
        await opportunity.save()
        if opportunity.category == "Black Belt":
            background_tasks.add_task(
                send_email,
                [employee.email],
                "CIRTS Portal : New Opportunity Assigned ",
                {
                    "user": f"{employee.name}",
                    "message": (
                        f"<p>You have been assigned to Opportunity <strong>{opportunity.opportunity_id}</strong> as a <strong>{team_member.role.upper()}</strong> by {opportunity.project_leader.name}({opportunity.project_leader.designation}).</p>"
                        f"<p>Please take a moment to review the details.</p>"
                    ),
                    "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                },
            )
        return team_member

    async def get(self, team_member_id: PydanticObjectId):
        team_member = await Opportunity.aggregate(
            [
                {"$unwind": "$team_members"},
                {"$match": {"team_members._id": ObjectId(team_member_id)}},
                {"$replaceRoot": {"newRoot": "$team_members"}},
            ]
        ).to_list()

        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "team member not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        res = parse_json(team_member)
        return res[0]

    async def update(self, data: TeamMemberRequest, team_member_id: PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        data = await Opportunity.find_one(
            ElemMatch(
                Opportunity.team_members, TeamMember.id == ObjectId(team_member_id)
            )
        )
        team_member = None
        for res in data.team_members:
            if str(res.id) == team_member_id:

                for key, value in values.items():
                    if value is not None and hasattr(res, key):
                        setattr(res, key, value)
                team_member = res

        await data.save()
        return team_member

    async def delete(self, team_member_id: PydanticObjectId):
        res = await Opportunity.find_one(
            ElemMatch(
                Opportunity.team_members, TeamMember.id == ObjectId(team_member_id)
            )
        )
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "team member not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [
            team_member
            for team_member in res.team_members
            if team_member.id != team_member_id
        ]
        res.team_members = data
        await res.save()


class DefinePhaseService:
    def __init__(self):
        pass

    async def create(self, data: DefinePhaseRequest, opportunity_id: PydanticObjectId):
        values = data.model_dump()
        opportunity = await Opportunity.find_one(Opportunity.id == opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        define_phase = DefinePhase(**values)
        await opportunity.set(
            {"define_phase": define_phase, "status": Status.DEFINE_PHASE_COMPLETED}
        )
        await opportunity.save()
        return opportunity.define_phase

    async def get(self, opportunity_id: PydanticObjectId):
        print(id)
        opportunity = await Opportunity.find_one(Opportunity.id == opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "define phase not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        return opportunity.define_phase

    async def update(self, data: DefinePhaseUpdate, opportunity_id: str):
        values = data.model_dump(exclude_none=True)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        for key, value in values.items():
            if value is not None and hasattr(data, key):
                setattr(opportunity.define_phase, key, value)

        await opportunity.save()
        print(opportunity.define_phase)
        return opportunity.define_phase


class SSVToolService:
    def __init__(self):
        pass

    async def create(
        self, data: list[SSVToolRequest], opportunity_id: PydanticObjectId
    ):
        values = [i.model_dump() for i in data]
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        if not opportunity.ssv_tools:
            data = [SSVToolBase(**value) for value in values]
            await opportunity.set(
                {
                    "ssv_tools": SSVTool(
                        data=data,
                    ),
                    "status": Status.SSV_TOOLS_UPDATED,
                }
            )

            await opportunity.save()
            return data
        else:
            data = opportunity.ssv_tools.data
            for value in values:
                data.append(SSVToolBase(**value))
            await opportunity.set(
                {
                    "ssv_tools": SSVTool(
                        data=data,
                    ),
                    "status": Status.SSV_TOOLS_UPDATED,
                }
            )

            await opportunity.save()
            return data
        
    async def update_ssv_tools(
         self, data: list[SSVToolRequest], opportunity_id: PydanticObjectId
     ):
        values = [i.model_dump() for i in data]
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [SSVToolBase(**value) for value in values]
        await opportunity.set(
                {
                    "ssv_tools": SSVTool(
                        data=data,
                    ),
                }
            )

        await opportunity.save()
        return data
       

    async def update(
        self,
        tool_id: PydanticObjectId,
        updated_data: SSVToolRequest,
        opportunity_id: PydanticObjectId,
    ):
        """Updates an existing SSVTool."""
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        if not opportunity.ssv_tools:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "No SSV tools found for this opportunity",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        updated = False
        for tool in opportunity.ssv_tools.data:
            if tool.id == tool_id:
                for key, value in updated_data.model_dump().items():
                    setattr(tool, key, value)
                updated = True
                break

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "SSV tool not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.save()
        return opportunity.ssv_tools

    async def delete(self, tool_id: PydanticObjectId, opportunity_id: PydanticObjectId):
        """Deletes an SSVTool from an opportunity."""
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        if not opportunity.ssv_tools:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "No SSV tools found for this opportunity",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        updated_data = [
            tool for tool in opportunity.ssv_tools.data if tool.id != tool_id
        ]

        if len(updated_data) == len(opportunity.ssv_tools.data):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "SSV tool not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        opportunity.ssv_tools.data = updated_data
        await opportunity.save()
        return {"message": "SSV tool deleted successfully", "success": True}

    async def update_document(self, opportunity_id: PydanticObjectId, document: str):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        opportunity.ssv_tools.document = document
        await opportunity.save()
        return opportunity.ssv_tools


class MeasureAnalysisService:
    def __init__(self):
        pass

    async def create(
        self,
        data: list[MeasureAnalysisRequest],
        opportunity_id: PydanticObjectId,
        status: str,
    ):
        values = [i.model_dump() for i in data]
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [MeasureAnalysisBase(**value) for value in values]

        await opportunity.set(
            {
                "measure_analysis_phase": MeasureAnalysisPhase(
                    data=data,
                    document=(
                        opportunity.measure_analysis_phase.document
                        if opportunity.measure_analysis_phase
                        else None
                    ),
                ),
                "status": (
                    Status.MEASURE_ANALYZE_PHASE_PENDING
                    if status == "Pending"
                    else Status.MEASURE_ANALYZE_PHASE_COMPLETED
                ),
            }
        )

        await opportunity.save()
        return data
    
    async def update_measure_analysis(
        self,
        data: list[MeasureAnalysisRequest],
        opportunity_id: PydanticObjectId,
    ):
        values = [i.model_dump() for i in data]
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [MeasureAnalysisBase(**value) for value in values]

        await opportunity.set(
            {
                "measure_analysis_phase": MeasureAnalysisPhase(
                    data=data,
                ),
               
            }
        )

        await opportunity.save()
        return data

    async def update(
        self,
        data: MeasureAnalysisRequest,
        opportunity_id: PydanticObjectId,
        tool_id: PydanticObjectId,
    ):
        values = data.model_dump(exclude_none=True)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        if not opportunity.measure_analysis_phase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "No Measure Analysis found for this opportunity",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        updated = False
        for tool in opportunity.measure_analysis_phase.data:
            if tool.id == tool_id:
                for key, value in values.items():
                    setattr(tool, key, value)
                updated = True
                break

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Measure Analysis not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.save()
        return opportunity.measure_analysis_phase

    async def delete(self, tool_id: PydanticObjectId, opportunity_id: PydanticObjectId):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        if not opportunity.measure_analysis_phase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "No Measure Analysis found for this opportunity",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        updated_data = [
            tool
            for tool in opportunity.measure_analysis_phase.data
            if tool.id != tool_id
        ]

        if len(updated_data) == len(opportunity.measure_analysis_phase.data):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Measure Analysis not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        opportunity.measure_analysis_phase.data = updated_data
        await opportunity.save()
        return {"message": "Measure Analysis deleted successfully", "success": True}

    async def update_document(self, opportunity_id: PydanticObjectId, document: str):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.set(
            {
                "measure_analysis_phase": MeasureAnalysisPhase(
                    document=document, data=opportunity.measure_analysis_phase.data
                ),
            }
        )
        await opportunity.save()
        return opportunity


class ImprovementService:
    def __init__(self):
        pass

    async def create(
        self,
        data: list[ImprovementRequest],
        opportunity_id: PydanticObjectId,
        status: str,
    ):
        values = [i.model_dump() for i in data]
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [ImprovementBase(**value) for value in values]

        await opportunity.set(
            {
                "improvement_phase": ImprovementPhase(
                    data=data,
                    document=(
                        opportunity.improvement_phase.document
                        if opportunity.improvement_phase
                        else None
                    ),
                ),
                "status": (
                    Status.IMPROVE_PHASE_PENDING
                    if status == "Pending"
                    else Status.IMPROVE_PHASE_COMPLETED
                ),
            }
        )

        await opportunity.save()
        return data
    
    async def update_improvement_phase(
        self,
        data: list[ImprovementRequest],
        opportunity_id: PydanticObjectId,
    ):
        values = [i.model_dump() for i in data]
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [ImprovementBase(**value) for value in values]

        await opportunity.set(
            {
                "improvement_phase": ImprovementPhase(
                    data=data,
                    document=(
                        opportunity.improvement_phase.document
                        if opportunity.improvement_phase
                        else None
                    ),
                ),
                
            }
        )

        await opportunity.save()
        return data

    async def update(
        self,
        data: ImprovementUpdate,
        opportunity_id: PydanticObjectId,
    ):
        values = data.model_dump(exclude_none=True)
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.set(
            {
                "improvement_phase": ImprovementPhase(
                    **values,
                    document=opportunity.improvement_phase.document,
                    data=opportunity.improvement_phase.data,
                ),
            }
        )

    async def update_document(self, opportunity_id: PydanticObjectId, document: str):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.set(
            {
                "improvement_phase": ImprovementPhase(
                    document=document,
                    data=opportunity.improvement_phase.data,
                    is_b_vs_c=opportunity.improvement_phase.is_b_vs_c,
                ),
            }
        )
        await opportunity.save()
        return opportunity


class ControlService:
    def __init__(self):
        pass

    async def create(
        self,
        data: list[ControlRequest],
        opportunity_id: PydanticObjectId,
        status: str,
    ):
        values = [i.model_dump() for i in data]
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [ControlBase(**value) for value in values]
        print(data)
        await opportunity.set(
            {
                "control_phase": ControlPhase(
                    data=data,
                    document=(
                        opportunity.control_phase.document
                        if opportunity.control_phase
                        else None
                    ),
                    control_response=(
                        opportunity.control_phase.control_response
                        if opportunity.control_phase
                        else None
                    ),
                    control_cost=(
                        opportunity.control_phase.control_cost
                        if opportunity.control_phase
                        else None
                    ),
                ),
                "status": (
                    Status.CONTROL_PHASE_PENDING
                    if status == "Pending"
                    else Status.CONTROL_PHASE_COMPLETED
                ),
            }
        )
        print(opportunity.control_phase)
        await opportunity.save()
        return opportunity.control_phase

    async def update(
        self,
        data: ControlUpdate,
        opportunity_id: PydanticObjectId,
    ):
        values = data.model_dump(exclude_none=True)
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.set(
            {
                "control_phase": ControlPhase(
                    **values,
                    data=opportunity.control_phase.data,
                    document=opportunity.control_phase.document,
                ),
            }
        )

        await opportunity.save()
        return opportunity
    
    
    async def update_control_phase(
        self,
        data: list[ControlRequest],
        opportunity_id: PydanticObjectId,
    ):
        values = [i.model_dump() for i in data]
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data = [ControlBase(**value) for value in values]
        print(data)
        await opportunity.set(
            {
                "control_phase": ControlPhase(
                    data=data,
                    document=(
                        opportunity.control_phase.document
                        if opportunity.control_phase
                        else None
                    ),
                    control_response=(
                        opportunity.control_phase.control_response
                        if opportunity.control_phase
                        else None
                    ),
                    control_cost=(
                        opportunity.control_phase.control_cost
                        if opportunity.control_phase
                        else None
                    ),
                ),
               
            }
        )
        print(opportunity.control_phase)
        await opportunity.save()
        return opportunity.control_phase

    async def update_document(self, opportunity_id: PydanticObjectId, document: str):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.set(
            {
                "control_phase": ControlPhase(
                    document=document,
                    data=opportunity.control_phase.data,
                    control_response=opportunity.control_phase.control_response,
                    control_cost=opportunity.control_phase.control_cost,
                ),
            }
        )
        await opportunity.save()
        return opportunity


class ProjectClosureService:
    def __init__(self):
        pass

    async def create(
        self,
        data: ProjectClosureRequest,
        opportunity_id: PydanticObjectId,
        background_tasks: BackgroundTasks,
    ):
        values = data.model_dump()

        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        print(data)
        await opportunity.set(
            {
                "project_closure": ProjectClosure(
                    **values,
                ),
                "status": (Status.PROJECT_CLOSURE_PENDING_CIHEAD),
            }
        )

        background_tasks.add_task(
            send_email,
            [opportunity.plant.ci_head.email],
            f"CIRTS Portal : Approval Requested For Opportunity {opportunity.opportunity_id} (CIRTS Portal) ",
            {
                "user": f"{opportunity.plant.ci_head.name}",
                "message": (
                    f"<p>The project closure has been submitted for Opportunity <strong>{opportunity.opportunity_id}</strong> by <strong>{opportunity.project_leader.name}</strong> "
                    f"({opportunity.project_leader.designation}).</p>"
                    f"<p>We kindly ask you to take a moment to review the details and approve the opportunity at your earliest convenience.</p>"
                ),
                "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
            },
        )

        return opportunity

    async def update(
        self, data: ProjectClosureUpdate, opportunity_id: PydanticObjectId
    ):
        values = data.model_dump(exclude_none=True)
        print(values)
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        for key, value in values.items():
            if value is not None and hasattr(data, key):
                setattr(opportunity.project_closure, key, value)

        await opportunity.save()
        return opportunity.project_closure


class MonthlySavingsService:
    def __init__(self):
        pass

    async def create(
        self, data: MonthlySavingsRequest, opportunity_id: PydanticObjectId
    ):
        values = data.model_dump()
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        print(opportunity.monthly_savings)

        monthly_savings = MonthlySavings(**values)
        opportunity.monthly_savings.append(monthly_savings)
        await opportunity.save()
        return monthly_savings
    
    
    
    async def get_monthly_savings(self, opportunity_id: PydanticObjectId):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        print(opportunity.monthly_savings)

        return opportunity.monthly_savings
    
    async def update_monthly_savings(self, opportunity_id: PydanticObjectId, monthly_savings_id : PydanticObjectId, data: MonthlySavingsUpdate,background_tasks : BackgroundTasks):
        opportunity = await Opportunity.get(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "opportunity not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        print(opportunity.monthly_savings)

        for index, monthly_savings in enumerate(opportunity.monthly_savings):
            print("Checking Monthly Savings:", monthly_savings)
            if str(monthly_savings.id) == str(monthly_savings_id):
                print("Found Matching Monthly Savings ID:", monthly_savings.id)

                for key, value in data.model_dump().items():
                    if value is not None and hasattr(monthly_savings, key):
                        setattr(monthly_savings, key, value)
                admins = await Employee.find(Employee.role == "admin").to_list()
                for admin in admins:
                    background_tasks.add_task(
                    send_email,
                    [admin.email],
                    f"CIRTS Portal: Monthy Savings For Opportunity ({opportunity.opportunity_id}) Approved By CS Head",
                    {
                        "user": f"{admin.name}",
                        "message": (
                            f" Monthy Savings of Rs{data.actual} for Opportunity <strong>{opportunity.opportunity_id}</strong> has been approved by CS Head {opportunity.plant.cs_head.name}.</p>"
                        ),
                        "frontend_url": f"{settings.FRONTEND_URL}/opportunity/{opportunity.id}",
                    },
                )
                break
            else:
                print("Not Matching Monthly Savings ID:", monthly_savings.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Monthly Savings not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await opportunity.save()
        return opportunity.monthly_savings
