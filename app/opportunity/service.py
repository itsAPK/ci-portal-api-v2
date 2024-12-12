from datetime import datetime
import json
import os
import shutil
from typing import Optional
from beanie import PydanticObjectId
from fastapi import File, HTTPException, UploadFile, status
from app.core.databases import parse_json
from app.employee.models import Employee
from app.opportunity.models import (
    ActionPlan,
    ActionPlanRequest,
    ActionPlanUpdate,
    DefinePhase,
    DefinePhaseRequest,
    DefinePhaseUpdate,
    Opportunity,
    OpportunityRequest,
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
from app.schemas.api import ResponseStatus
from beanie.operators import ElemMatch

from bson import ObjectId, json_util

from app.utils.upload import save_file


DEPARTMENT_KPI_PATH = "uploads/define-phase/department-kpi"
LAST_SIX_TREND_PATH = "uploads/define-phase/last-six-trend"
ISO_PLOT_PATH = "uploads/define-phase/iso-plot"
CONCENTRATION_CHART_PATH = "uploads/define-phase/concentration-chart"
PROCESS_FLOW_DIAGRAM_PATH = "uploads/define-phase/process-flow-diagram"

class OppurtunityService:
    def __init__(self):
        pass

    async def create(self, data: OpportunityRequest, created_by: Employee):
        values = data.model_dump()
        print(values)
        count = await Opportunity.find(
            Opportunity.plant == values["plant"],
            Opportunity.opportunity_year
            == f"{datetime.now().year}-{datetime.now().year + 1}",
        ).count()
        opportunity_id = f"{values['plant']}/{values['category']}/{datetime.now().year}-{datetime.now().year + 1}/{count + 1}"
        opportunity = Opportunity(
            **values,
            opportunity_id=opportunity_id,
            created_by=created_by,
            status=Status.OPEN_FOR_ASSIGNING,
        )
        await opportunity.insert()
        return opportunity
    
    async def calculate_impact_score(self, opportunity : OpportunityRequest):
        baseline = [
            {
                "name": "<=10,000 ppm",
                "score" : 0.2,
                "weightage" : 15
            },
            {
                "name": ">10,000 and <=30,000 ppm",
                "score" : 0.6,
                "weightage" : 15
            },
            {
                "name": ">30,000 and <=100,000 ppm",
                "score" : 0.8,
                "weightage" : 15
            },
            {
                "name": ">100,000 ppm",
                "score" : 1.0,
                "weightage" : 15
            }
        ]
        
        cross_function_rating = [
            {
                "name": "Low",
                "score" : 0.2,
                "weightage" : 10
            },
            {
                "name": "Medium",
                "score" : 0.5,
                "weightage" : 10
            },
            {
                "name": "High",
                "score" : 1,
                "weightage" : 10
            },
        ]
        
        data_analysis = [
            {
                "name": "No Data",
                "score" : 0.1,
                "weightage" : 15
            },
            {
                "name": "Less Data",
                "score" : 0.4,
                "weightage" : 15
            },
            {
                "name": "Medium Data",
                "score" : 0.7,
                "weightage" : 15
            },
            {
                "name": "Data Intensive",
                "score" : 1,
                "weightage" : 15
            }
        ]
        
        project_nature = [
            {
                "name": "Problem Solving",
                "score" : 0.2,
                "weightage" : 10
            },
            {
                "name": "Process Optimization",
                "score" : 0.6,
                "weightage" : 10
            },
            {
                "name": "Innovation",
                "score" : 0.8,
                "weightage" : 10
            },
            {
                "name": "Perceived Quality",
                "score" : 1,
                "weightage" : 10
            }
        ]
        
        expected_savings = [
            {
                "name": "<= 1 Lakh",
                "score" : 0.2,
                "weightage" : 10
            },
            {
                "name": ">1 and <=5 Lakh",
                "score" : 0.6,
                "weightage" : 10
            },
            {
                "name": ">5 and <=10 Lakh",
                "score" : 0.8,
                "weightage" : 10
            },
            {
                "name" : ">10 Lakh",
                "score" : 1,
                "wightage" : 10
                
            }
            
        ]
        
        external_customer = [
            {
                "name" : "Nil",
                "score" : 0,
                "wightage" : 0
            },
            {
                "name" : "Low",
                "score" : 0.2,
                "wightage" : 10
            },
            {
                "name" : "Medium",
                "score" : 0.5,
                "wightage" : 10
            },
            {
                "name" : "High",
                "score" : 1,
                "wightage" : 10
            }
        ]
        
        internal_customer = [
            {
                "name" : "Nil",
                "score" : 0,
                "wightage" : 0
            },
            {
                "name" : "Low",
                "score" : 0.2,
                "wightage" : 10
            },
            {
                "name" : "Medium",
                "score" : 0.5,
                "wightage" : 10
            },
            {
                "name" : "High",
                "score" : 1,
                "wightage" : 10
            }
        ]
        
        project_type = [
            {
                "name" : "Type -1",
                "score" : 0.4,
                "wightage" : 15
            },
            {
                "name" : "Type -2",
                "score" : 0.6,
                "wightage" : 15
            },
            {
                "name" : "Type -3",
                "score" : 0.8,
                "wightage" : 15
            },
            {
                "name" : "Type -4",
                "score" : 1,
                "wightage" : 15
            }
        ]
        

    async def assign_project_leader(
        self, opportunity_id: PydanticObjectId, employee_id: PydanticObjectId
    ):
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
        employee = await Employee.find_one(Employee.id == employee_id)
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
        opportunity.set({"project_leader": employee, "status": Status.PROJECT_ASSIGN_PENDING_HOD})

        await opportunity.save()
        return opportunity

    async def get(self, opportunity_id: PydanticObjectId):
        opportunity = await Opportunity.find_one(
            Opportunity.opportunity_id == opportunity_id
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
        print(results)
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

    async def update(self, data: OpportunityRequest, id: PydanticObjectId):
        values = data.model_dump(exclude_none=True)
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
        for key, value in values.items():
            if value is not None and hasattr(opportunity, key):
                setattr(opportunity, key, value)

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
        values = data.model_dump(exclude_none=True)
        print(values)
        data = await Opportunity.find_one(
            ElemMatch(
                Opportunity.action_plan, ActionPlan.id == ObjectId(action_plan_id)
            )
        )
        action_plan = None
        for res in data.action_plan:
            if str(res.id) == action_plan_id:

                for key, value in values.items():
                    if value is not None and hasattr(res, key):
                        setattr(res, key, value)
                action_plan = res

        await data.save()
        return action_plan

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

    async def create(self, data: TeamMemberRequest, opportunity_id: str):
        values = data.model_dump()
        employee = await Employee.find_one(
            Employee.employee_id == values["employee_id"]
        )
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
        if len(opportunity.team_members) == 0:
            await opportunity.set({"status": Status.TEAMS_UPDATED})
        await opportunity.team_members.append(team_member)
        await opportunity.save()
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
            {"define_phase": define_phase, "status": Status.DEFINE_PHASE_PENDING}
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
        for key, value in values.items():
            if value is not None and hasattr(data, key):
                setattr(opportunity.define_phase, key, value)

        await opportunity.save()
        print(opportunity.define_phase)
        return opportunity.define_phase
    
    

class SSVToolService:
    def __init__(self):
        pass
    
    async def create(self, data: SSVToolRequest, opportunity_id: PydanticObjectId):
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
        if not opportunity.ssv_tools:
            data = SSVToolBase(**values)
            await opportunity.set({"ssv_tools": SSVTool(
                data=[data],
                ), "status": Status.DEFINE_PHASE_COMPLETED})
            
            await opportunity.save()
            return data
        else:
            data = opportunity.ssv_tools.data
            data.append(SSVToolBase(**values))
            await opportunity.set({"ssv_tools": SSVTool(
                data=data,
                ), "status": Status.DEFINE_PHASE_COMPLETED})
            
            await opportunity.save()
            return data
       
