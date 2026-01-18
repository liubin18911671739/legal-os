from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from app.models.contract import ContractType, ContractStatus
import uuid


class ContractBase(BaseModel):
    """Base contract schema."""
    contract_type: ContractType
    parties: Dict[str, Any]
    amount: Optional[Decimal] = None
    currency: str = "CNY"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ContractCreate(ContractBase):
    """Schema for creating a contract."""
    document_id: uuid.UUID


class ContractUpdate(BaseModel):
    """Schema for updating a contract."""
    contract_type: Optional[ContractType] = None
    parties: Optional[Dict[str, Any]] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ContractStatus] = None


class ContractResponse(ContractBase):
    """Schema for contract response."""
    id: uuid.UUID
    document_id: uuid.UUID
    status: ContractStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
