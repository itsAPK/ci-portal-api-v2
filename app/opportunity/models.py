from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime

from app.employee.models import Employee
from app.plant.models import Plant
from app.schemas.db import BaseDocument

from enum import Enum

class Status(str, Enum):
    OPEN_FOR_ASSIGNING = "Open for Assigning"
    PROJECT_ASSIGNED = "Project Assigned"
    DETAILS_UPDATED = "Details Updated"
    TEAMS_UPDATED = "Teams Updated"
    OPPORTUNITY_COMPLETED = "Opportunity Completed"
    REVOKE = "Revoke"
    DEFINE_PHASE_COMPLETED = "Define Phase Completed"
    SSV_TOOLS_UPDATED = "SSV's Tools Updated"
    MEASURE_ANALYZE_PHASE_PENDING = "Measure & Analyze Phase Pending"
    MEASURE_ANALYZE_PHASE_COMPLETED = "Measure & Analyze Phase Completed"
    IMPROVE_PHASE_PENDING = "Improvement Phase Pending"
    IMPROVE_PHASE_COMPLETED = "Improvement Phase Completed"
    CONTROL_PHASE_PENDING = "Control Phase Pending"
    CONTROL_PHASE_COMPLETED = "Control Phase Completed"
    CLOSURE_COMPLETED = "Closure Completed"
    PROJECT_CLOSURE_PENDING_CIHEAD = "Project Closure Pending (CIHead)"
    PROJECT_CLOSURE_PENDING_HOD = "Project Closure Pending (HOD)"
    PROJECT_CLOSURE_PENDING_LOF = "Project Closure Pending (LOF)"
    PROJECT_CLOSURE_PENDING_COSTING_HEAD = "Project Closure Pending (Costing Head)"
    PROJECT_COMPLETED = "Project Completed"
    EXPIRED = "Expired"


    
class Opportunity(BaseDocument, BaseModel):
    opportunity_id: str
    company : str
    department : str
    bussiness_unit : str
    plant: Plant
    category : str
    statement : str
    expected_savings : str 
    project_type : str | None = None
    project_nature : str | None = None
    internal_customer_impact : str | None = None
    external_customer_impact  : str | None = None
    data_analysis : str | None = None
    cross_ratio : str | None = None
    baseline : str | None = None
    status : Optional[Status] = Field(default=Status.OPEN_FOR_ASSIGNING)
    project_score : Optional[float] = Field(default=0.0)
    project_impact : Optional[str] = None
    project_leader : Optional[Employee] =  None
    remarks : Optional[str]  = None
    savings_type : Optional[str] = None
    estimated_savings : Optional[float] = Field(default=0.0)
    opportunity_year: str = Field(default_factory=lambda: f"{datetime.now().year}-{datetime.now().year + 1}")
    created_by : Employee
    action_plan: list["ActionPlan"] = []
    team_members: list["TeamMember"] = []
    schedules: list["Schedule"] = []
    define_phase : Optional['DefinePhase'] = None
    ssv_tools : Optional['SSVTool'] = None
    control_phase : Optional['ControlPhase'] = None
    improvement_phase : Optional['ImprovementPhase'] = None
    measure_analysis_phase : Optional['MeasureAnalysisPhase'] = None
    project_closure : Optional['ProjectClosure'] = None
    monthly_savings : list['MonthlySavings'] = [] 
    file : list[str] = []
    is_approved_by_ci_head : Optional[bool] = None
    is_approved_by_hod : Optional[bool] = None
    is_approved_by_lof : Optional[bool] = None
    is_approved_by_cs_head : Optional[bool] = None
    start_date : Optional[datetime] = None
    end_date : Optional[datetime] = None
    sub_category : Optional[str] = None
    a3_file : Optional[str] = None
    
class OpportunityRequest(BaseModel):
    company : str
    department : str
    bussiness_unit : str
    plant: PydanticObjectId
    category : str
    statement : str
    project_type : Optional[str] = None
    project_nature : Optional[str] = None
    internal_customer_impact : Optional[str] = None
    external_customer_impact  : Optional[str] = None
    data_analysis : Optional[str] = None
    cross_ratio : Optional[str] = None
    project_impact : Optional[str] = None
    project_score : Optional[float] = None
    expected_savings : str
    baseline : Optional[str] = None
    start_date : Optional[datetime] = None
    end_date : Optional[datetime] = None
    sub_category : Optional[str] = None
    estimated_savings : Optional[float] = None
    a3_file : Optional[str] = None

    
class OpportunityUpdate(BaseModel):
    company : Optional[str] = None
    department : Optional[str] = None
    bussiness_unit : Optional[str] = None
    plant: Optional[PydanticObjectId] = None
    category : Optional[str] = None
    statement : Optional[str] = None
    project_type : Optional[str] = None
    project_nature : Optional[str] = None
    internal_customer_impact : Optional[str] = None
    external_customer_impact  : Optional[str] = None
    data_analysis : Optional[str] = None
    cross_ratio : Optional[str] = None
    expected_savings : Optional[str] = None 
    baseline : Optional[str] = None
    estimated_savings : Optional[float] = None
    opportunity_year : Optional[str] = None
    project_score : Optional[float] = None
    project_impact : Optional[str] = None
    project_leader : Optional[Employee] = None
    remarks : Optional[str] = None
    savings_type : Optional[str] = None
    status : Optional[Status] = None
    file : list[str] = []
    start_date : Optional[datetime] = None
    end_date : Optional[datetime] = None
    sub_category : Optional[str] = None
    a3_file : Optional[str] = None

    

class ActionPlanStatus(str, Enum):
    IN_PROCESS = "In Process"
    COMPLETED = "Completed"
    REFERRED = "Referred"
    FOR_INFO = "For Info"
    
class AssignProjectLeaderRequest(BaseModel):
    opportunity_id :  PydanticObjectId
    employee_id : PydanticObjectId
    
class ActionPlan(Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    created_at : datetime = datetime.now()
    action : str 
    status : Optional[ActionPlanStatus] = ActionPlanStatus.IN_PROCESS
    target_date : datetime
    findings : Optional[str] = None
    
    
class ActionPlanRequest(BaseModel):
    action : str 
    target_date : datetime
    
class ActionPlanUpdate(BaseModel):
    action : Optional[str] = None
    status : Optional[ActionPlanStatus] = None
    target_date : Optional[datetime] = None
    findings : Optional[str] = None
    
    
class TeamMemberRole(str, Enum):
    PROJECT_MENTOR = "Project Mentor"
    TEAM_MEMBER = "Team Member"
    PROJECT_SPONSOR = "Project Sponsor"

class TeamMember(Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    employee: Employee
    role: TeamMemberRole = TeamMemberRole.TEAM_MEMBER
    
class TeamMemberRequest(BaseModel):
    employee_id: PydanticObjectId
    role: TeamMemberRole = TeamMemberRole.TEAM_MEMBER


    
class Schedule(Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    planned_start_date : datetime
    planned_end_date : datetime
    actual_start_date : Optional[datetime] = None
    actual_end_date : Optional[datetime] = None
    phase : str
    
class ScheduleRequest(BaseModel):
    planned_start_date : datetime
    planned_end_date : datetime
    phase : str

class ScheduleUpdate(BaseModel):
    planned_start_date : Optional[datetime] = None
    planned_end_date : Optional[datetime] = None
    actual_start_date : Optional[datetime] = None
    actual_end_date : Optional[datetime] = None
    phase : Optional[str] = None
    

    
class DefinePhase(Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    part_no : str
    baseline : str 
    target : str
    baseline_uom : Optional[str] = None
    target_uom : Optional[str] = None   
    part_having_problem : str
    part_not_having_problem : str
    suspected_phenomenon : str
    last_manufacturing : str
    no_machines : int
    no_streams : int
    response_type : str
    process_stage : str
    specification : Optional[str] = None
    max_value_of_baseline : int
    min_value_of_baseline : int
    conculsion : str
    is_conecentration : bool
    is_audited : bool
    max_month : str
    min_month : str
    is_iso_plot : bool
    is_p_chart_done : bool
    abnormalities : bool
    abnormalities_audited_tool_conditions : Optional[bool] = False
    is_audited_tool_conditions : bool
    department_kpi_path :Optional[str] = None
    process_flow_diagram : Optional[str] = None
    last_six_months_trend : Optional[str] = None
    iso_plot : Optional[str] = None
    concentration_chart : Optional[str] = None
    p_chart : Optional[str] = None
    
    quick_win_for_abnormalities : Optional[str] = None
    quick_win_for_tool_conditions : Optional[str] = None
   
class DefinePhaseRequest(BaseModel):
    part_no : str
    baseline : str 
    target : str
    baseline_uom : Optional[str] = None
    target_uom : Optional[str] = None  
    part_having_problem : str
    part_not_having_problem : str
    suspected_phenomenon : str
    last_manufacturing : str
    no_machines : int
    specification : Optional[str] = None
    no_streams : int
    response_type : str
    process_stage : str
    max_value_of_baseline : int
    min_value_of_baseline : int
    conculsion : str
    is_conecentration : bool
    is_audited : bool
    max_month : str
    min_month : str
    is_iso_plot : bool
    is_p_chart_done : bool
    abnormalities : bool
    abnormalities_audited_tool_conditions :bool
    is_audited_tool_conditions : bool
    department_kpi_path :Optional[str] = None
    process_flow_diagram : Optional[str] = None
    last_six_months_trend : Optional[str] = None
    iso_plot : Optional[str] = None
    concentration_chart : Optional[str] = None
    p_chart : Optional[str] = None
    iso_plot : Optional[str] = None
    quick_win_for_abnormalities : Optional[str] = None
    quick_win_for_tool_conditions : Optional[str] = None
    

class DefinePhaseUpdate(BaseModel):
    part_no : Optional[str] = None
    baseline : Optional[str] = None
    target : Optional[str] = None
    baseline_uom : Optional[str] = None
    target_uom : Optional[str] = None  
    part_having_problem : Optional[str] = None
    part_not_having_problem : Optional[str] = None
    suspected_phenomenon : Optional[str] = None
    last_manufacturing : Optional[str] = None
    no_machines : Optional[int] = None
    no_streams : Optional[int] = None
    specification : Optional[str] = None
    base_uom : Optional[str] = None
    target_uom : Optional[str] = None
    response_type : Optional[str] = None
    process_stage : Optional[str] = None
    max_value_of_baseline : Optional[int] = None
    min_value_of_baseline : Optional[int] = None
    conculsion : Optional[str] = None
    is_conecentration : Optional[bool] = None
    is_audited : Optional[bool] = None
    max_month : Optional[str] = None
    min_month : Optional[str] = None
    department_kpi_path :Optional[str] = None
    process_flow_diagram : Optional[str] = None
    last_six_months_trend : Optional[str] = None
    iso_plot : Optional[str] = None
    concentration_chart : Optional[str] = None
    is_iso_plot : Optional[bool] = None
    p_chart : Optional[str] = None
    abnormalities : Optional[bool] = None
    is_audited_tool_conditions : Optional[bool] = None
    quick_win_for_abnormalities : Optional[str] = None
    quick_win_for_tool_conditions : Optional[str] = None
    abnormalities_audited_tool_conditions : Optional[bool] = None
class SSVToolBase( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    suspected_source : str
    tools : list[str] 
    type_of_ssv : str
    
class SSVTool( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list["SSVToolBase"] = []
    document : Optional[str] = None
    
class SSVToolRequest(BaseModel):
    suspected_source : str
    tools : list[str] 
    type_of_ssv : str


class SSVToolUpdate(BaseModel):
    suspected_source : Optional[str] = None
    tools : Optional[list[str]] = None
    type_of_ssv : Optional[str] = None

    
class MeasureAnalysisBase( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    suspected_source : str
    tools : list[str] 
    root_cause : Optional[str] = None
    tool_id : PydanticObjectId
    
class MeasureAnalysisPhase( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list["MeasureAnalysisBase"] = []
    document : Optional[str] = None
    
class MeasureAnalysisRequest(BaseModel):
    suspected_source : str
    tools : list[str] 
    root_cause : Optional[str] = None
    tool_id : PydanticObjectId


class MeasureAnalysisUpdate(BaseModel):
    suspected_source : Optional[str] = None
    tools : Optional[list[str]] = None
    root_cause : Optional[str] = None
    document : Optional[str] = None
    
class ImprovementBase( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    confirmed_cause : str
    measure_analysis_id : PydanticObjectId
    action_taken : Optional[str] = None
    type_of_action : Optional[str] = None
    
class ImprovementPhase( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list["ImprovementBase"] = []
    is_b_vs_c : Optional[bool] = None
    document : Optional[str] = None
    
class ImprovementRequest(BaseModel):
    confirmed_cause : str
    action_taken : Optional[str] = None
    type_of_action : Optional[str] = None
    measure_analysis_id : PydanticObjectId

class ImprovementUpdate(BaseModel):
    
    is_b_vs_c : Optional[bool] = None
 
    
class ControlBase( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    confirmed_cause : str
    mechanism : Optional[str] = None
    contol_tools : Optional[str] = None
    improvement_id : PydanticObjectId
    
class ControlResponse( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    baseline : str
    target : str
    actual : str
    uom : str

class ControlCost( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    estimated: int
    actual : int
    uom : str
    
class ControlPhase( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list["ControlBase"] = []
    control_response : Optional["ControlResponse"] = None
    control_cost : Optional["ControlCost"] = None
    document : Optional[str] = None
    
class ControlRequest(BaseModel):
    confirmed_cause : str
    mechanism : Optional[str] = None
    contol_tools : Optional[str] = None
    improvement_id : PydanticObjectId
    
class ControlUpdate(BaseModel):
    data : Optional[list["ControlBase"]] = None
    control_response : Optional["ControlResponse"] = None
    control_cost : Optional["ControlCost"] = None
    document : Optional[str] = None
    
    
class ProjectClosure( Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    suspected_cause : list[str] = []
    pin_pointed_root_cause : list[str] = []
    actions_implemented : list[str] = []
    tools_used : list[str] = []
    tangible_benifits : str
    intangible_benifits : str
    horizantal_deployment : str
    standardization : str
    estimated_savings : str
    closure_document : Optional[str] = None
    before_improvement :  Optional[str] = None
    after_improvement :  Optional[str] = None
    success_rate : str
    
    
class ProjectClosureRequest(BaseModel):
    suspected_cause : list[str] = []
    pin_pointed_root_cause : list[str] = []
    actions_implemented : list[str] = []
    tools_used : list[str] = []
    tangible_benifits : str
    intangible_benifits : str
    horizantal_deployment : str
    standardization : str
    estimated_savings : str 
    success_rate : str
    
class ProjectClosureUpdate(BaseModel):
    suspected_cause : Optional[list[str]] = None
    pin_pointed_root_cause : Optional[list[str]] = None
    actions_implemented : Optional[list[str]] = None
    tools_used : Optional[list[str]] = None
    tangible_benifits : Optional[str] = None
    intangible_benifits : Optional[str] = None
    horizantal_deployment : Optional[str] = None
    standardization : Optional[str] = None
    estimated_savings : Optional[str] = None
    closure_document : Optional[str] = None
    before_improvement : Optional[str] = None
    after_improvement : Optional[str] = None
    estimated_savings : Optional[str] = None
    
    
class MonthlySavings(Document):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    year : str
    month : str
    savings : str
    is_approved : bool | None = None
    actual : str | None = None
    
class MonthlySavingsRequest(BaseModel):
    year : str
    month : str
    savings : str
    
    
class MonthlySavingsUpdate(BaseModel):
    year : Optional[str] = None
    month : Optional[str] = None
    savings : Optional[str] = None
    is_approved : Optional[bool] = None
    actual : Optional[str] = None   