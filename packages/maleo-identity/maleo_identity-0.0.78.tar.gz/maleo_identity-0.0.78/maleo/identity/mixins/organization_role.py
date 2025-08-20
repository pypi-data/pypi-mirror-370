from pydantic import BaseModel, Field
from maleo.soma.mixins.parameter import Expand as BaseExpand
from maleo.identity.enums.organization_role import ExpandableField


class Expand(BaseExpand[ExpandableField]):
    pass


class Key(BaseModel):
    key: str = Field(..., max_length=50, description="Organization role's key")


class Name(BaseModel):
    name: str = Field(..., max_length=50, description="Organization role's name")
