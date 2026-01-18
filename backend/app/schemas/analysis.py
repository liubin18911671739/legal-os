from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.analysis_result import AnalysisStatus, RiskLevel
import uuid


class AnalysisResultBase(BaseModel):
    """Base analysis result schema."""
    contract_id: uuid.UUID


class AnalysisResultCreate(AnalysisResultBase):
    """Schema for creating an analysis result."""
    task_id: Optional[uuid.UUID] = None
    analysis_data: Optional[Dict[str, Any]] = None
    review_data: Optional[Dict[str, Any]] = None
    validation_data: Optional[Dict[str, Any]] = None
    report_markdown: Optional[str] = None
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    risk_level: Optional[RiskLevel] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[AnalysisStatus] = None


class AnalysisResultUpdate(BaseModel):
    """Schema for updating an analysis result."""
    analysis_data: Optional[Dict[str, Any]] = None
    review_data: Optional[Dict[str, Any]] = None
    validation_data: Optional[Dict[str, Any]] = None
    report_markdown: Optional[str] = None
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    risk_level: Optional[RiskLevel] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[AnalysisStatus] = None
    error_message: Optional[str] = None


class AnalysisResultResponse(BaseModel):
    """Schema for analysis result response."""
    id: uuid.UUID
    contract_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    analysis_data: Optional[Dict[str, Any]] = None
    review_data: Optional[Dict[str, Any]] = None
    validation_data: Optional[Dict[str, Any]] = None
    report_markdown: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[RiskLevel] = None
    confidence: Optional[float] = None
    status: AnalysisStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
