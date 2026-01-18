from sqlalchemy import Column, String, Text, Integer, Float, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel


class AnalysisStatus(str, enum.Enum):
    """Analysis status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    """Risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalysisResult(BaseModel):
    """Model for storing contract analysis results."""
    
    __tablename__ = "analysis_results"
    
    contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    analysis_data = Column(JSON, nullable=True)
    review_data = Column(JSON, nullable=True)
    validation_data = Column(JSON, nullable=True)
    report_markdown = Column(Text, nullable=True)
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(
        Enum(RiskLevel),
        nullable=True,
        index=True,
    )
    confidence = Column(Float, nullable=True)
    status = Column(
        Enum(AnalysisStatus),
        default=AnalysisStatus.PENDING,
        index=True,
    )
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, risk_level='{self.risk_level}', status='{self.status}')>"
