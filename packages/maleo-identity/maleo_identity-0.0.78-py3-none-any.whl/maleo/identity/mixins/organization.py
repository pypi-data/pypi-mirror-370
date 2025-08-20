from pydantic import BaseModel, Field
from maleo.soma.mixins.parameter import Expand as BaseExpand
from maleo.identity.enums.organization import ExpandableField


class Expand(BaseExpand[ExpandableField]):
    pass


class Key(BaseModel):
    key: str = Field(..., max_length=255, description="Organization's key")


class Name(BaseModel):
    name: str = Field(..., max_length=255, description="Organization's name")
