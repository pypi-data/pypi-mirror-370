from enum import StrEnum


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    USERNAME = "username"
    EMAIL = "email"


class ExpandableField(StrEnum):
    USER_TYPE = "user_type"
    SYSTEM_ROLES = "system_roles"
    SYSTEM_ROLE_DETAILS = "system_roles.system_role_details"
    PROFILE = "profile"
    GENDER = "profile.gender"
    BLOOD_TYPE = "profile.blood_type"
