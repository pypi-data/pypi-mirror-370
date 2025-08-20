from pydantic import BaseModel, Field
from maleo.soma.types.base import OptionalString


class RegisterMetadata(BaseModel):
    organization_key: OptionalString = Field(..., description="Organization's key")
