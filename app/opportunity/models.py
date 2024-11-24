from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime

from app.employee.models import Employee
from app.schemas.db import BaseDocument

from enum import Enum

class Status(str, Enum):
    OPEN_FOR_ASSIGNING = "Open for Assigning"
    PROJECT_ASSIGN_PENDING_CIHEAD = "Project Assign Pending (CIHead)"
    PROJECT_ASSIGN_PENDING_HOD = "Project Assign Pending (HOD)"
    PL_APPROVED = "PL Approved"
    DETAILS_UPDATED = "Details Updated"
    TEAMS_UPDATED = "Teams Updated"
    OPPORTUNITY_COMPLETED = "Opportunity Completed"
    DEFINE_COMPLETED = "Define Completed"
    REVOKE = "Revoke"
    DEFINE_PHASE_PENDING = "Define Phase Pending"
    DEFINE_PHASE_COMPLETED = "Define Phase Completed"
    MEASURE_ANALYZE_PHASE_PENDING = "Measure/Analyze Phase Pending"
    MEASURE_ANALYZE_PHASE_COMPLETED = "Measure/Analyze Phase Completed"
    IMPROVE_PHASE_PENDING = "Improve Phase Pending"
    IMPROVE_PHASE_COMPLETED = "Improve Phase Completed"
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
    division: str
    category : str
    statement : str
    project_type : str
    project_nature : str
    internal_customer_impact : str
    external_customer_impact  : str
    data_analysis : str
    cross_ratio : str
    expected_savings : str
    baseline : str
    status : Optional[Status] = Field(default=Status.OPEN_FOR_ASSIGNING)
    project_score : Optional[float] = Field(default=0.0)
    project_impact : Optional[str] 
    project_leader : Optional[Employee]
    remarks : Optional[str]
    savings_type : Optional[str]
    estimated_savings : Optional[float] = Field(default=0.0)
    opportunity_year : str = Field(default=f"{datetime.now().year}-{datetime.now().year + 1}")
    created_by : Employee
    action_plan: list["ActionPlan"] = []
    team_members: list["TeamMember"] = []
    schedules: list["Schedule"] = []
    define_phase : Optional['DefinePhase'] = None
    control_phase : Optional['ControlPhase'] = None
    improvement_phase : Optional['ImprovementPhase'] = None
    measure_analysis_phase : Optional['MeasureAnalysisPhase'] = None
    
    
class OpportunityRequest(BaseModel):
    company : str
    department : str
    bussiness_unit : str
    division: str
    category : str
    statement : str
    project_type : str
    project_nature : str
    internal_customer_impact : str
    external_customer_impact  : str
    data_analysis : str
    cross_ratio : str
    expected_savings : str
    baseline : str
    
class OpportunityUpdate(BaseModel):
    company : Optional[str] = None
    department : Optional[str] = None
    bussiness_unit : Optional[str] = None
    division: Optional[str] = None
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
    

class ActionPlanStatus(str, Enum):
    IN_PROCESS = "In Process"
    COMPLETED = "Completed"
    DEFERRED = "Deferred"
    FOR_INFO = "For Info"
    
class ActionPlan(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    created_at : datetime = datetime.now()
    action : str 
    status : Optional[ActionPlanStatus] = ActionPlanStatus.IN_PROCESS
    target_date : datetime
    findings : Optional[str] = None
    
    
class ActionPlanRequest(BaseModel):
    action : str 
    target_date : datetime
    opportunity_id : str
    
class ActionPlanUpdate(BaseModel):
    action : Optional[str] = None
    status : Optional[ActionPlanStatus] = None
    target_date : Optional[datetime] = None
    findings : Optional[str] = None
    
    
class TeamMemberRole(str, Enum):
    PROJECT_MENTOR = "Project Mentor"
    TEAM_MEMBER = "Team Member"
    PROJECT_SPONSOR = "Project Sponsor"

class TeamMember(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    employee: Employee
    role: TeamMemberRole = TeamMemberRole.TEAM_MEMBER
    
class TeamMemberRequest(BaseModel):
    employee: Employee
    role: TeamMemberRole = TeamMemberRole.TEAM_MEMBER


    
class Schedule(BaseModel):
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
    

    
class DefinePhase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    part_no : str
    baseline : int 
    target : int
    part_having_problem : str
    part_not_having_problem : str
    suspected_phenomenon : str
    last_manufacturing : str
    no_line : int
    no_streams : int
    base_uom : str
    target_uom : str
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
    department_kpi_path :Optional[str] = None
    process_flow_diagram : Optional[str] = None
    last_six_months_trend : Optional[str] = None
    iso_plot : Optional[str] = None
    concentration_chart : Optional[str] = None
   
class DefinePhaseRequest(BaseModel):
    part_no : str
    baseline : int 
    target : int
    part_having_problem : str
    part_not_having_problem : str
    suspected_phenomenon : str
    last_manufacturing : str
    no_line : int
    no_streams : int
    base_uom : str
    target_uom : str
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
    department_kpi_path :Optional[str] = None
    process_flow_diagram : Optional[str] = None
    last_six_months_trend : Optional[str] = None
    iso_plot : Optional[str] = None
    concentration_chart : Optional[str] = None

class DefinePhaseUpdate(BaseModel):
    part_no : Optional[str] = None
    baseline : Optional[int] = None
    target : Optional[int] = None
    part_having_problem : Optional[str] = None
    part_not_having_problem : Optional[str] = None
    suspected_phenomenon : Optional[str] = None
    last_manufacturing : Optional[str] = None
    no_line : Optional[int] = None
    no_streams : Optional[int] = None
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
    
class SSVToolBase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    suspected_source : str
    tools : str
    
class SSVTool(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list["SSVToolBase"] = []
    document : Optional[str] = None
    
class SSVToolRequest(BaseModel):
    suspected_source : str
    tools : str

class SSVToolUpdate(BaseModel):
    suspected_source : Optional[str] = None
    tools : Optional[str] = None
    document : Optional[str] = None
    
class MeasureAnalysisBase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    suspected_source : str
    tools : str
    root_cause : str
    
class MeasureAnalysisPhase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list["MeasureAnalysisBase"] = []
    document : Optional[str] = None
    
class MeasureAnalysisRequest(BaseModel):
    suspected_source : str
    tools : str
    root_cause : str

class MeasureAnalysisUpdate(BaseModel):
    suspected_source : Optional[str] = None
    tools : Optional[str] = None
    root_cause : Optional[str] = None
    document : Optional[str] = None
    
class ImprovementBase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    confirmed_cause : str
    action_taken : str
    type_of_action : str
    
class ImprovementPhase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list["ImprovementBase"] = []
    is_b_vs_c : bool
    document : Optional[str] = None
    
class ImprovementRequest(BaseModel):
    confirmed_cause : str
    action_taken : str
    type_of_action : str

class ImprovementUpdate(BaseModel):
    confirmed_cause : Optional[str] = None
    action_taken : Optional[str] = None
    type_of_action : Optional[str] = None
    is_b_vs_c : Optional[bool] = None
    document : Optional[str] = None
    
class ControlBase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    confirmed_cause : str
    mechanism : str
    contol_tools : str
    
class ControlResponse(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    baseline : int
    target : int
    action : int
    uom : str

class ControlCost(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    estimated: int
    actual : int
    uom : str
    
class ControlPhase(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    data : list[ControlBase] = []
    control_response : Optional["ControlResponse"] = None
    control_cost : Optional["ControlCost"] = None
    document : Optional[str] = None
    
    
class ProjectClosure(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    suspected_cause : list[str] = []
    pin_pointed_root_cause : list[str] = []
    actions_implemented : list[str] = []
    tools_used : str
    tangible_benifits : str
    intangible_benifits : str
    horizantal_deployment : str
    standardization : str
    closure_document : str
    before_improvement : str
    after_improvement : str