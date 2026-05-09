from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeStatus(str, Enum):
    CANDIDATE = "candidate"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


class SourceType(str, Enum):
    SOP = "sop"
    WORKER_CONVERSATION = "worker_conversation"
    SUPERVISOR_REVIEW = "supervisor_review"
    SYSTEM = "system"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class KnowledgeCreate(BaseModel):
    entity: str = Field(..., description="Main object, machine, station, material, or process")
    claim: str = Field(..., description="The operational knowledge claim")
    condition: Optional[str] = Field(default=None, description="When this knowledge applies")
    recommendation: Optional[str] = Field(default=None, description="Recommended action")
    source_type: SourceType = Field(default=SourceType.WORKER_CONVERSATION)
    source_text: Optional[str] = Field(default=None, description="Original transcript or source text")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: KnowledgeStatus = Field(default=KnowledgeStatus.CANDIDATE)
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    conflict_group_id: Optional[str] = None


class KnowledgeUpdate(BaseModel):
    entity: Optional[str] = None
    claim: Optional[str] = None
    condition: Optional[str] = None
    recommendation: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    status: Optional[KnowledgeStatus] = None
    risk_level: Optional[RiskLevel] = None
    conflict_group_id: Optional[str] = None


class KnowledgeRead(BaseModel):
    id: str
    entity: str
    claim: str
    condition: Optional[str]
    recommendation: Optional[str]
    source_type: SourceType
    source_text: Optional[str]
    confidence: float
    status: KnowledgeStatus
    risk_level: RiskLevel
    conflict_group_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
    
    
class ConversationIngestRequest(BaseModel):
    conversation_id: str
    worker_id: str
    transcript: str


class ExtractedKnowledge(BaseModel):
    entity: str
    claim: str
    condition: Optional[str] = None
    recommendation: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    conflict_group_id: Optional[str] = None
    

class IngestConversationResponse(BaseModel):
    knowledge: KnowledgeRead
    verification_status: KnowledgeStatus
    verification_reason: str
    conflicting_item_id: Optional[str] = None