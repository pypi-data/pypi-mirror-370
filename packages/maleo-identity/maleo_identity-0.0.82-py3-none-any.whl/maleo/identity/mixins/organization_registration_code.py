from pydantic import BaseModel, Field
from uuid import UUID
from maleo.soma.types.base import OptionalInteger


class Code(BaseModel):
    code: UUID = Field(..., description="Registration code")


class MaxUses(BaseModel):
    max_uses: int = Field(1, ge=1, description="Max code uses")


class OptionalMaxUses(BaseModel):
    max_uses: OptionalInteger = Field(None, ge=1, description="Max code uses")


class CurrentUses(BaseModel):
    current_uses: int = Field(0, ge=0, description="Current code uses")
