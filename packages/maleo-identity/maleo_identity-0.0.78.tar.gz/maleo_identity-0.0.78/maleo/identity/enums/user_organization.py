from enum import StrEnum


class ExpandableField(StrEnum):
    USER = "user"
    USER_TYPE = "user_type"
    SYSTEM_ROLES = "system_roles"
    SYSTEM_ROLE_DETAILS = "system_roles.system_role_details"
    PROFILE = "profile"
    GENDER = "profile.gender"
    BLOOD_TYPE = "profile.blood_type"
    ORGANIZATION = "organization"
    ORGANIZATION_TYPE = "organization.organization_type"
    REGISTRATION_CODE = "organization.registration_code"
