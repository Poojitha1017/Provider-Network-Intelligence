from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    GenericAuthResponse,
    AuthUserResponse,
)
from app.services.auth_service import auth_service
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=GenericAuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    Register a new user in Supabase Auth. Sends email confirmation.
    """
    return auth_service.signup(request)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user credentials with Supabase Auth and return session bearer token.
    """
    return auth_service.login(request)


@router.post("/logout", response_model=GenericAuthResponse)
async def logout():
    """
    Terminate session and sign out user.
    """
    return auth_service.logout()


@router.post("/forgot-password", response_model=GenericAuthResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Trigger Supabase Auth password reset email.
    """
    return auth_service.forgot_password(request)


@router.get("/me", response_model=AuthUserResponse)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve profile details for the authenticated user.
    """
    return AuthUserResponse(
        id=current_user["id"],
        email=current_user["email"],
        fullName=current_user.get("fullName", current_user["email"]),
        mobile=current_user.get("user_metadata", {}).get("mobile"),
        organization=current_user.get("user_metadata", {}).get("organization"),
        role=current_user.get("role", "Network Manager"),
    )
