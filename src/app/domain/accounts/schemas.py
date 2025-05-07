from app.lib.schema import BaseStruct

__all__ = ("AccountRegister",)


class AccountRegister(BaseStruct):
    """Account Register."""

    user_type: int
    email_1: str
    email_2: str | None
    password: str
    first_name: str
    middle_name: str | None
    last_name: str
