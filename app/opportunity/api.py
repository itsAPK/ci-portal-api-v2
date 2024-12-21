from typing import Optional
from beanie import PydanticObjectId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from app.employee.models import Employee, Role
from app.opportunity.models import (
    ActionPlanRequest,
    ActionPlanUpdate,
    AssignProjectLeaderRequest,
    ControlRequest,
    ControlUpdate,
    DefinePhaseRequest,
    DefinePhaseUpdate,
    ImprovementRequest,
    ImprovementUpdate,
    MeasureAnalysisRequest,
    OpportunityRequest,
    OpportunityUpdate,
    ProjectClosureRequest,
    ProjectClosureUpdate,
    SSVToolRequest,
    ScheduleRequest,
    ScheduleUpdate,
    TeamMemberRequest,
)
from app.opportunity.service import (
    CONCENTRATION_CHART_PATH,
    CONTROL_PATH,
    DEPARTMENT_KPI_PATH,
    ISO_PLOT_PATH,
    LAST_SIX_TREND_PATH,
    MEASURE_ANALYSIS_PATH,
    OPPORTUNITY_CATEGORY_PATH,
    P_CHART,
    PROCESS_FLOW_DIAGRAM_PATH,
    SSV_TOOL_PATH,
    IMPROVEMENT_PATH,
    PROJECT_CLOSURE_PATH,
    ProjectClosureService,
    ActionPlanService,
    ControlService,
    DefinePhaseService,
    MeasureAnalysisService,
    OppurtunityService,
    ProjectScheduleService,
    SSVToolService,
    TeamMemberService,
    ImprovementService,
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
    _team_member_service: TeamMemberService = Depends(TeamMemberService)
    _define_phase_service: DefinePhaseService = Depends(DefinePhaseService)
    _ssv_tool_service: SSVToolService = Depends(SSVToolService)
    _measure_analysis_service: MeasureAnalysisService = Depends(MeasureAnalysisService)
    _improvement_service: ImprovementService = Depends(ImprovementService)
    _control_service: ControlService = Depends(ControlService)
    _project_closure_service: ProjectClosureService = Depends(ProjectClosureService)

    @opportunity_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(
        self, opportunity: OpportunityRequest, background_tasks: BackgroundTasks
    ):
        print(self.user)
        result = await self._service.create(
            opportunity, created_by=self.user, background_tasks=background_tasks
        )
        return Response(
            message="Opportunity Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post("/assign-project-leader", status_code=status.HTTP_200_OK)
    async def assign_project_leader(
        self, data: AssignProjectLeaderRequest, background_tasks: BackgroundTasks
    ):

        result = await self._service.assign_project_leader(
            data.opportunity_id, data.employee_id, background_tasks=background_tasks
        )
        return Response(
            message="Assign Project Leader Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, opportunity: OpportunityUpdate):
        result = await self._service.update(opportunity, id)
        return Response(
            message="Opportunity Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        print(id)
        result = await self._service.delete(id)
        return Response(
            message="Opportunity Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @opportunity_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
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
        
    @opportunity_router.post("/export", status_code=status.HTTP_200_OK)
    async def export(self, data: FilterRequest, page: int = 1, page_size: int = 10):
        result = await self._service.export_query(data.filter)
        return Response(
            message="Opportunity Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @opportunity_router.get("/approve/{opportunity_id}", status_code=status.HTTP_200_OK)
    async def approve(self, opportunity_id: PydanticObjectId, role: str,background_tasks: BackgroundTasks):
        result = await self._service.approve(opportunity_id, self.user.id, role,background_tasks)
        return Response(
            message="Opportunity Approved Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.post(
        "/upload/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_opportunity_file(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(
            file.file, OPPORTUNITY_CATEGORY_PATH, filename=file.filename
        )
        result = await self._service.update(
            data=OpportunityUpdate(file=file_path),
            id=opportunity_id,
        )
        return Response(
            message="Define Phase Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/action-plan/{opportunity_id}", status_code=status.HTTP_201_CREATED
    )
    async def create_action_plan(
        self, data: ActionPlanRequest, opportunity_id: PydanticObjectId
    ):
        result = await self._action_plan_service.create(data, opportunity_id)
        return Response(
            message="Action Plan Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get("/action-plan/{id}", status_code=status.HTTP_200_OK)
    async def get_action_plan(self, id: PydanticObjectId):
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
    async def update_action_plan(
        self, action_plan_id: PydanticObjectId, data: ActionPlanUpdate
    ):
        result = await self._action_plan_service.update(data, action_plan_id)
        return Response(
            message="Action Plan Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete("/action-plan/{id}", status_code=status.HTTP_200_OK)
    async def delete_action_plan(self, id: PydanticObjectId):
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
    async def create_schedule(
        self, opportunity_id: PydanticObjectId, data: ScheduleRequest
    ):
        result = await self._schedule_service.create(data, opportunity_id)
        return Response(
            message="Schedule Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get("/schedule/{schedule_id}", status_code=status.HTTP_200_OK)
    async def get_schedule(self, schedule_id: PydanticObjectId):
        result = await self._schedule_service.get(schedule_id)
        return Response(
            message="Schedule Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @opportunity_router.patch("/schedule/{schedule_id}", status_code=status.HTTP_200_OK)
    async def update_schedule(
        self, schedule_id: PydanticObjectId, data: ScheduleUpdate
    ):
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
    async def delete_schedule(self, schedule_id: PydanticObjectId):
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
    async def create_team_member(
        self,
        data: TeamMemberRequest,
        opportunity_id: PydanticObjectId,
        background_tasks: BackgroundTasks,
    ):
        result = await self._team_member_service.create(
            data=data, opportunity_id=opportunity_id, background_tasks=background_tasks
        )
        return Response(
            message="Team Member Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.get(
        "/team-member/{team_member_id}", status_code=status.HTTP_200_OK
    )
    async def get_team_member(self, team_member_id: PydanticObjectId):
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
    async def update_team_member(
        self, team_member_id: PydanticObjectId, data: TeamMemberRequest
    ):
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
    async def delete_team_member(self, team_member_id: PydanticObjectId):
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
        "/define-phase/upload/p-chart/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_p_chart_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, P_CHART, filename=file.filename)
        result = await self._define_phase_service.update(
            data=DefinePhaseUpdate(p_chart=file_path),
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
            data=DefinePhaseUpdate(process_flow_diagram=file_path),
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
            data=DefinePhaseUpdate(last_six_months_trend=file_path),
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
            data=DefinePhaseUpdate(iso_plot=file_path),
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
            data=DefinePhaseUpdate(concentration_chart=file_path),
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
        data: list[SSVToolRequest],
    ):
        result = await self._ssv_tool_service.create(data, opportunity_id)
        return Response(
            message="SSV Tool Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.patch(
        "/ssv-tool/{opportunity_id}/{tool_id}", status_code=status.HTTP_200_OK
    )
    async def update_ssv_tool(
        self,
        opportunity_id: PydanticObjectId,
        tool_id: PydanticObjectId,
        data: SSVToolRequest,
    ):
        result = await self._ssv_tool_service.update(tool_id, data, opportunity_id)
        return Response(
            message="SSV Tool Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete(
        "/ssv-tool/{opportunity_id}/{tool_id}", status_code=status.HTTP_200_OK
    )
    async def delete_ssv_tool(
        self,
        opportunity_id: PydanticObjectId,
        tool_id: PydanticObjectId,
    ):
        result = await self._ssv_tool_service.delete(tool_id, opportunity_id)
        return Response(
            message="SSV Tool Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @opportunity_router.post(
        "/ssv-tool/upload/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_ssv_tool_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, SSV_TOOL_PATH, filename=file.filename)
        result = await self._ssv_tool_service.update_document(
            opportunity_id=opportunity_id,
            document=file_path,
        )
        return Response(
            message="SSV Tool Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/measure-analysis/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_measure_analysis(
        self,
        opportunity_id: PydanticObjectId,
        data: list[MeasureAnalysisRequest],
        status: str,
    ):
        result = await self._measure_analysis_service.create(
            data, opportunity_id, status
        )
        return Response(
            message="Measure Analysis Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.patch(
        "/measure-analysis/{opportunity_id}/{tool_id}",
        status_code=status.HTTP_200_OK,
    )
    async def update_measure_analysis(
        self,
        opportunity_id: PydanticObjectId,
        tool_id: PydanticObjectId,
        data: MeasureAnalysisRequest,
    ):
        result = await self._measure_analysis_service.update(
            data, opportunity_id, tool_id
        )
        return Response(
            message="Measure Analysis Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.delete(
        "/measure-analysis/{opportunity_id}/{tool_id}",
        status_code=status.HTTP_200_OK,
    )
    async def delete_measure_analysis(
        self,
        opportunity_id: PydanticObjectId,
        tool_id: PydanticObjectId,
    ):
        result = await self._measure_analysis_service.delete(tool_id, opportunity_id)
        return Response(
            message="Measure Analysis Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @opportunity_router.post(
        "/measure-analysis/upload/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_measure_analysis_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, MEASURE_ANALYSIS_PATH, filename=file.filename)
        result = await self._measure_analysis_service.update_document(
            opportunity_id=opportunity_id,
            document=file_path,
        )
        return Response(
            message="Measure Analysis Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/improvement/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_improvement(
        self,
        opportunity_id: PydanticObjectId,
        data: list[ImprovementRequest],
        status: str,
    ):
        result = await self._improvement_service.create(data, opportunity_id, status)
        return Response(
            message="Improvement Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.patch(
        "/improvement/{opportunity_id}",
        status_code=status.HTTP_200_OK,
    )
    async def update_improvement(
        self,
        opportunity_id: PydanticObjectId,
        data: ImprovementUpdate,
    ):
        result = await self._improvement_service.update(data, opportunity_id)
        return Response(
            message="Improvement Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.post(
        "/improvement/upload/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_improvement_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, IMPROVEMENT_PATH, filename=file.filename)
        result = await self._improvement_service.update_document(
            opportunity_id=opportunity_id,
            document=file_path,
        )
        return Response(
            message="Improvement Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/control/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_control(
        self,
        opportunity_id: PydanticObjectId,
        data: list[ControlRequest],
        status: str,
    ):
        result = await self._control_service.create(data, opportunity_id, status)
        return Response(
            message="Control Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.patch(
        "/control/{opportunity_id}",
        status_code=status.HTTP_200_OK,
    )
    async def update_control(
        self,
        opportunity_id: PydanticObjectId,
        data: ControlUpdate,
    ):
        result = await self._control_service.update(data, opportunity_id)
        return Response(
            message="Control Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.post(
        "/control/upload/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_control_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, CONTROL_PATH, filename=file.filename)
        result = await self._control_service.update_document(
            opportunity_id=opportunity_id,
            document=file_path,
        )
        return Response(
            message="Control Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/project-closure/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def create_project_closure(
        self,
        opportunity_id: PydanticObjectId,
        data: ProjectClosureRequest,
        background_tasks: BackgroundTasks,
    ):
        result = await self._project_closure_service.create(data, opportunity_id, background_tasks=background_tasks)
        return Response(
            message="Project Closure Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.patch(
        "/project-closure/{opportunity_id}",
        status_code=status.HTTP_200_OK,
    )
    async def update_project_closure(
        self,
        opportunity_id: PydanticObjectId,
        data: ProjectClosureUpdate,
    ):
        result = await self._project_closure_service.update(data, opportunity_id)
        return Response(
            message="Project Closure Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @opportunity_router.post(
        "/project-closure/upload/closure-document/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_project_closure_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, PROJECT_CLOSURE_PATH, filename=file.filename)
        result = await self._project_closure_service.update(
            data=ProjectClosureUpdate(closure_document=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="Project Closure Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/project-closure/upload/before-improvement/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_before_improvement_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, PROJECT_CLOSURE_PATH, filename=file.filename)
        result = await self._project_closure_service.update(
            data=ProjectClosureUpdate(before_improvement=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="Before Improvement Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @opportunity_router.post(
        "/project-closure/upload/after-improvement/{opportunity_id}",
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_after_improvement_document(
        self,
        opportunity_id: PydanticObjectId,
        file: UploadFile = File(...),
    ):
        file_path = save_file(file.file, PROJECT_CLOSURE_PATH, filename=file.filename)
        result = await self._project_closure_service.update(
            data=ProjectClosureUpdate(after_improvement=file_path),
            opportunity_id=opportunity_id,
        )
        return Response(
            message="After Improvement Document Uploaded Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
