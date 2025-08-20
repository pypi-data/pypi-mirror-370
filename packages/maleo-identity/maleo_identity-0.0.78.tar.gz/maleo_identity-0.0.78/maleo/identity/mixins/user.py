from pydantic import BaseModel, Field
from uuid import UUID
from maleo.soma.mixins.parameter import Expand as BaseExpand
from maleo.soma.types.base import OptionalListOfStrings
from maleo.identity.enums.user import ExpandableField


class Expand(BaseExpand[ExpandableField]):
    pass


class Username(BaseModel):
    username: str = Field(..., max_length=50, description="User's username")


class OptionalListOfUsernames(BaseModel):
    usernames: OptionalListOfStrings = Field(None, description="Specific usernames")


class Email(BaseModel):
    email: str = Field(..., max_length=255, description="User's email")


class OptionalListOfEmails(BaseModel):
    emails: OptionalListOfStrings = Field(None, description="Specific emails")


class Phone(BaseModel):
    phone: str = Field(..., min_length=4, max_length=15, description="User's phone")


class OptionalListOfPhones(BaseModel):
    phones: OptionalListOfStrings = Field(None, description="Specific phones")


class Password(BaseModel):
    password: str = Field(..., max_length=255, description="User's password")


class PasswordConfirmation(BaseModel):
    password_confirmation: str = Field(
        ..., max_length=255, description="User's password confirmation"
    )


class RegistrationCode(BaseModel):
    registration_code: UUID = Field(..., description="Registration code")
