from __future__ import annotations

from litestar import Controller, post

from app.domain.accounts import urls
from app.domain.accounts.schemas import AccountRegister


class AuthController(Controller):
    """AuthController."""

    tags = ["Authentication"]

    @post(path=urls.ACCOUNT_REGISTER)
    async def signup(self, data: AccountRegister) -> str:
        """Signup."""
        print(data.to_dict())
        return "dummy"
