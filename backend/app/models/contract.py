from sqlalchemy import Column, String, Numeric, Date, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel
from sqlalchemy.orm import relationship


class ContractType(str, enum.Enum):
    """Contract types."""
    SALES = "sales"
    PURCHASE = "purchase"
    SERVICE = "service"
    NDA = "nda"
    EMPLOYMENT = "employment"
    OTHER = "other"


class ContractStatus(str, enum.Enum):
    """Contract status."""
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class Contract(BaseModel):
    """Contract model for storing contract information."""
    
    __tablename__ = "contracts"
    
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contract_type = Column(
        Enum(ContractType),
        nullable=False,
        index=True,
    )
    parties = Column(JSON, nullable=False)
    amount = Column(Numeric(20, 2), nullable=True)
    currency = Column(String(3), default="CNY")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(
        Enum(ContractStatus),
        default=ContractStatus.DRAFT,
        index=True,
    )
    
    # Relationship
    document = relationship("Document", back_populates="contracts")
    
    def __repr__(self):
        return f"<Contract(id={self.id}, type='{self.contract_type}', amount={self.amount})>"
