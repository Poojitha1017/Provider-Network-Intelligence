from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    fullName: str = Field(..., description="User's full name")
    mobile: Optional[str] = None
    organization: Optional[str] = None
    role: str = Field("Network Manager", description="User role")


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6)


class AuthUserResponse(BaseModel):
    id: str
    email: str
    fullName: str
    mobile: Optional[str] = None
    organization: Optional[str] = None
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class GenericAuthResponse(BaseModel):
    success: bool
    message: str
