from .DataModel import DataObjectTypeEnum as DataObjectTypeEnum
from dataclasses import dataclass
from strenum import StrEnum

class DocumentTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Other = 'Other'
    ObserverNotes = 'ObserverNotes'
    LoadSheet = 'LoadSheet'
    ProcessingNotes = 'ProcessingNotes'
    ProjectBid = 'ProjectBid'
    SurveyPlat = 'SurveyPlat'
    Contract = 'Contract'
    DrillingReport = 'DrillingReport'
    DrillingDiagram = 'DrillingDiagram'
    DrillingPlan = 'DrillingPlan'
    AFE = 'AFE'
    JointOperatingAgreement = 'JointOperatingAgreement'
    DivisionOrder = 'DivisionOrder'
    RevenueStatement = 'RevenueStatement'
    JointInterestBill = 'JointInterestBill'
    OperatingInvoice = 'OperatingInvoice'
    RoyaltyStatement = 'RoyaltyStatement'
    GasBalancingStatement = 'GasBalancingStatement'
    CrudeOilRunTicket = 'CrudeOilRunTicket'
    LeaseOperatingStatement = 'LeaseOperatingStatement'
    Regulatory = 'Regulatory'
    EnvironmentalImpactStatement = 'EnvironmentalImpactStatement'
    Presentation = 'Presentation'
    Permit = 'Permit'

class ActivityTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Acquisition = 'Acquisition'
    Exploration = 'Exploration'
    Drilling = 'Drilling'
    Completion = 'Completion'
    Production = 'Production'
    Recompletion = 'Recompletion'
    Abandonment = 'Abandonment'

class DisciplineTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Engineering = 'Engineering'
    Geoscience = 'Geoscience'
    Land = 'Land'
    Accounting = 'Accounting'
    Legal = 'Legal'
    Corporate = 'Corporate'
    Marketing = 'Marketing'
    Drilling = 'Drilling'
    Completions = 'Completions'
    Geosteering = 'Geosteering'

class ConfidenceTypeEnum(StrEnum):
    Unknown = 'Unknown'
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'

@dataclass
class Document:
    id: int = ...
    row_version: str | None = ...
    name: str | None = ...
    file_size: int = ...
    description: str | None = ...
    owner_type: DataObjectTypeEnum = ...
    owner_id: int = ...
    path: str = ...
    author: str | None = ...
    document_type: DocumentTypeEnum = ...
    activity: ActivityTypeEnum = ...
    discipline: DisciplineTypeEnum = ...
    confidence: ConfidenceTypeEnum = ...
    def is_valid(self) -> bool: ...
    def set_path(self, file_name: str, relative_path: str = ''): ...
