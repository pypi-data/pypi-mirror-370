from enum import StrEnum


class IdentifierType(StrEnum):
    USER_ID = "user_id"
    ID_CARD = "id_card"


class ValidImageMimeType(StrEnum):
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    PNG = "image/png"


class ExpandableField(StrEnum):
    GENDER = "gender"
    BLOOD_TYPE = "blood_type"
