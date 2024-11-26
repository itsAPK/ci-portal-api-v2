from typing import Optional
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.employee.models import Employee, Role
from app.opportunity.models import (
    ActionPlanRequest,
    ActionPlanUpdate,
    DefinePhaseRequest,
    DefinePhaseUpdate,
    OpportunityRequest,
    OpportunityUpdate,
    SSVToolRequest,
    ScheduleRequest,
    ScheduleUpdate,
    TeamMemberRequest,
)
from app.opportunity.service import (
    CONCENTRATION_CHART_PATH,
    DEPARTMENT_KPI_PATH,
    ISO_PLOT_PATH,
    LAST_SIX_TREND_PATH,
    PROCESS_FLOW_DIAGRAM_PATH,
    ActionPlanService,
    DefinePhaseService,
    OppurtunityService,
    ProjectScheduleService,
    SSVToolService,
)
from app.schemas.api import FilterRequest, Response, ResponseStatus
from app.utils.class_based_views import cbv
from app.core.security import authenticate
from app.utils.upload import save_file

opportunity_router = APIRouter()


@cbv(opportunity_router)
class OpportunityRouter:
    user: Employee = Depends(authenticate)
    _service: OppurtunityService = Depends(OppurtunityService)
    _action_plan_service: ActionPlanService = Depends(ActionPlanService)
    _schedule_service: ProjectScheduleService = Depends(ProjectScheduleService)
    _define_phase_service: DefinePhaseService = Depends(DefinePhaseService)
    _ssv_tool_service: SSVToolService = Depends(SSVToolService)

    @opportunity_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, opportunity: OpportunityRequest):
        print(self.user)
        result = await self._service.create(opportunity, created_by=self.user)
        return Response(
            message="Opportunity Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get(
        "/assign-project-leader/{opportunity_id}", status_code=status.HTTP_200_OK
    )
    async def assign_project_leader(self, opportunity_id: str):
        if self.user.role != Role.project_leader:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Only project lead can assign project lead",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        result = await self._service.assign_project_leader(opportunity_id, self.user.id)
        return Response(
            message="Assign Project Leader Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: str, opportunity: OpportunityUpdate):
        result = await self._service.update(opportunity, id)
        return Response(
            message="Opportunity Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: str):
        result = await self._service.delete(id)
        return Response(
            message="Opportunity Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @opportunity_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: str):
        result = await self._service.get(id)
        return Response(
            message="Opportunity Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @opportunity_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self, page: int = 1, page_size: int = 10):
        result = await self._service.get_all(page, page_size)
        return Response(
            message="Opportunity Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @opportunity_router.post("/query", status_code=status.HTTP_200_OK)
    async def query(self, data: FilterRequest, page: int = 1, page_size: int = 10):
        result = await self._service.query(data.filter, page, page_size)
        return Response(
            message="Opportunity Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @opportunity_router.post(
        "/action-plan/{opportunity_id}", status_code=status.HTTP_201_CREATED
    )
    async def create_action_plan(self, data: ActionPlanRequest, opportunity_id: str):
        result = await self._action_plan_service.create(data, opportunity_id)
        return Response(
            message="Action Plan Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get("/action-plan/{id}", status_code=status.HTTP_200_OK)
    async def get_action_plan(self, id: str):
        result = await self._action_plan_service.get(id)
        print(result)
        return Response(
            message="Action Plan Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @opportunity_router.patch(
        "/action-plan/{action_plan_id}", status_code=status.HTTP_200_OK
    )
    async def update_action_plan(self, action_plan_id: str, data: ActionPlanUpdate):
        result = await self._action_plan_service.update(data, action_plan_id)
        return Response(
            message="Action Plan Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete("/action-plan/{id}", status_code=status.HTTP_200_OK)
    async def delete_action_plan(self, id: str):
        result = await self._action_plan_service.delete(id)
        return Response(
            message="Action Plan Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @opportunity_router.post(
        "/schedule/{opportunity_id}", status_code=status.HTTP_201_CREATED
    )
    async def create_schedule(self, opportunity_id: str, data: ScheduleRequest):
        result = await self._schedule_service.create(data, opportunity_id)
        return Response(
            message="Schedule Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get("/schedule/{schedule_id}", status_code=status.HTTP_200_OK)
    async def get_schedule(self, schedule_id: str):
        result = await self._schedule_service.get(schedule_id)
        return Response(
            message="Schedule Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @opportunity_router.patch("/schedule/{schedule_id}", status_code=status.HTTP_200_OK)
    async def update_schedule(self, schedule_id: str, data: ScheduleUpdate):
        result = await self._schedule_service.update(data, schedule_id)
        return Response(
            message="Schedule Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete(
        "/schedule/{schedule_id}", status_code=status.HTTP_200_OK
    )
    async def delete_schedule(self, schedule_id: str):
        result = await self._schedule_service.delete(schedule_id)
        return Response(
            message="Schedule Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @opportunity_router.post(
        "/team-member/{opportunity_id}", status_code=status.HTTP_201_CREATED
    )
    async def create_team_member(self, data: TeamMemberRequest, opportunity_id: str):
        result = await self._team_member_service.create(data, opportunity_id)
        return Response(
            message="Team Member Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get(
        "/team-member/{team_member_id}", status_code=status.HTTP_200_OK
    )
    async def get_team_member(self, team_member_id: str):
        result = await self._team_member_service.get(team_member_id)
        return Response(
            message="Team Member Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @opportunity_router.patch(
        "/team-member/{team_member_id}", status_code=status.HTTP_200_OK
    )
    async def update_team_member(self, team_member_id: str, data: TeamMemberRequest):
        result = await self._team_member_service.update(data, team_member_id)
        return Response(
            message="Team Member Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete(
        "/team-member/{team_member_id}", status_code=status.HTTP_200_OK
    )
    async def delete_team_member(self, team_member_id: str):
        result = await self._team_member_service.delete(team_member_id)
        return Response(
            message="Team Member Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @opportunity_router.post(
        "/define-phase/{opportunity_id}", status_code=status.HTTP_201_CREATED
    )
    async def create_define_phase(
        self, data: DefinePhaseRequest, opportunity_id: PydanticObjectId
    ):
        result = await self._define_phase_service.create(data, opportunity_id)
        return Response(
            message="Define Phase Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get(
        "/define-phase/{opportunity_id}", status_code=status.HTTP_200_OK
    )
    async def get_define_phase(self, opportunity_id: PydanticObjectId):
        result = await self._define_phase_service.get(opportunity_id)
        return Response(
            message="Define Phase Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @opportunity_router.patch(
        "/define-phase/{opportunity_id}", status_code=status.HTTP_200_OK
    )
    async def update_define_phase(
        self, opportunity_id: PydanticObjectId, data: DefinePhaseUpdate
    ):
        result = await self._define_phase_service.update(data, opportunity_id)
        return Response(
            message="Define Phase Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.post(
        "/define-phase/upload/department-kpi/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_department_kpi_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, DEPARTMENT_KPI_PATH, filename=file.filename)
        result = await self._define_phase_service.update(
            data=DefinePhaseUpdate(department_kpi_path=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="Define Phase Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/define-phase/upload/process-flow-diagram/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_process_flow_diagram_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(
            file.file, PROCESS_FLOW_DIAGRAM_PATH, filename=file.filename
        )
        result = await self._define_phase_service.update(
            data=DefinePhaseUpdate(process_flow_diagram_path=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="Define Phase Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/define-phase/upload/last-six-months-trend/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_last_six_months_trend_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, LAST_SIX_TREND_PATH, filename=file.filename)
        result = await self._define_phase_service.update(
            data=DefinePhaseUpdate(last_six_trend_path=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="Define Phase Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/define-phase/upload/iso-plot/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_iso_plot_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, ISO_PLOT_PATH, filename=file.filename)
        result = await self._define_phase_service.update(
            data=DefinePhaseUpdate(iso_plot_path=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="Define Phase Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/define-phase/upload/concentration-chart/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_concentration_chart_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(
            file.file, CONCENTRATION_CHART_PATH, filename=file.filename
        )
        result = await self._define_phase_service.update(
            data=DefinePhaseUpdate(concentration_chart_path=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="Define Phase Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/ssv-tool/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_ssv_tool(
        self,
        opportunity_id: PydanticObjectId,
        data: SSVToolRequest,
    ):
        result = await self._ssv_tool_service.create(data, opportunity_id)
        return Response(
            message="SSV Tool Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )