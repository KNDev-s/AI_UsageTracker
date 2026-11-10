from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    type: Literal["individual", "team"] = "individual"
    timezone: str = Field(default="America/Sao_Paulo", min_length=1, max_length=64)
    currency: str = Field(default="BRL", min_length=3, max_length=8)


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    currency: str | None = Field(default=None, min_length=3, max_length=8)


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: str
    owner_user_id: UUID
    timezone: str
    currency: str
    created_at: datetime
    role: str | None = None


class MembershipOut(BaseModel):
    id: UUID
    account_id: UUID
    user_id: UUID
    role: str
    status: str
    created_at: datetime
    user_email: str
    user_full_name: str

