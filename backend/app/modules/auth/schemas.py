from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.modules.accounts.schemas import AccountOut
from app.modules.users.schemas import UserOut


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=200)
    timezone: str = Field(default="America/Sao_Paulo", min_length=1, max_length=64)
    currency: str = Field(default="BRL", min_length=3, max_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=10, max_length=512)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10, max_length=512)
    new_password: str = Field(min_length=8, max_length=128)


class AuthSessionOut(BaseModel):
    user: UserOut
    accounts: list[AccountOut]
    active_account_id: UUID | None = None
    google_oauth_enabled: bool = False

