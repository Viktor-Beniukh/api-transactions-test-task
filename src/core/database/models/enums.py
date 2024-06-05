from enum import StrEnum


class Role(StrEnum):
    """
    Roles users.
    """
    admin: str = "admin"
    user: str = "user"
