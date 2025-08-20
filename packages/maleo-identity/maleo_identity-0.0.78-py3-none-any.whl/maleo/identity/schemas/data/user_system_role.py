from pydantic import BaseModel, Field
from typing import List
from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.soma.mixins.general import UserId
from maleo.metadata.schemas.data.system_role import (
    SimpleSystemRoleMixin,
    OptionalExpandedSystemRoleMixin,
)


class UserSystemRoleDataSchema(
    OptionalExpandedSystemRoleMixin,
    SimpleSystemRoleMixin,
    UserId,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


class ListOfUserSystemRolesDataMixin(BaseModel):
    system_roles: List[UserSystemRoleDataSchema] = Field(
        [], description="User system roles"
    )
