from maleo.soma.mixins.general import UserId
from maleo.identity.mixins.user_profile import (
    IdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    FullName,
    BirthPlace,
    BirthDate,
    AvatarName,
)


class UserProfileDTO(
    AvatarName,
    BirthDate,
    BirthPlace,
    FullName,
    EndingTitle,
    LastName,
    MiddleName,
    FirstName,
    LeadingTitle,
    IdCard,
    UserId,
):
    pass
