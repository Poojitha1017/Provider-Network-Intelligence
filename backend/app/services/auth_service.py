import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.db.supabase import get_supabase_client
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthUserResponse,
    TokenResponse,
    GenericAuthResponse,
)

logger = logging.getLogger("uvicorn.error")

# In-memory dev store for demo/fallback when Supabase keys are not yet provided
_DEV_ACCOUNTS: Dict[str, Dict[str, Any]] = {}


class AuthService:
    @staticmethod
    def signup(request: SignupRequest) -> GenericAuthResponse:
        """
        Signs up a new user via Supabase Auth and sends verification email.
        """
        client = get_supabase_client()
        if client:
            try:
                response = client.auth.sign_up(
                    {
                        "email": request.email,
                        "password": request.password,
                        "options": {
                            "data": {
                                "fullName": request.fullName,
                                "mobile": request.mobile,
                                "organization": request.organization,
                                "role": request.role,
                            }
                        },
                    }
                )
                if response and response.user:
                    return GenericAuthResponse(
                        success=True,
                        message="Signup successful. Please verify your email to log in.",
                    )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Signup failed. Please check user details.",
                )
            except Exception as e:
                logger.error(f"Supabase auth signup error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                )

        # Fallback local in-memory
        if request.email in _DEV_ACCOUNTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )

        _DEV_ACCOUNTS[request.email] = {
            "id": f"user_{len(_DEV_ACCOUNTS) + 1}",
            "email": request.email,
            "password": request.password,
            "fullName": request.fullName,
            "mobile": request.mobile,
            "organization": request.organization,
            "role": request.role,
        }
        return GenericAuthResponse(
            success=True,
            message="Signup successful. (Development mode)",
        )

    @staticmethod
    def login(request: LoginRequest) -> TokenResponse:
        """
        Authenticates user with Supabase Auth and returns access session token.
        """
        client = get_supabase_client()
        if client:
            try:
                response = client.auth.sign_in_with_password(
                    {
                        "email": request.email,
                        "password": request.password,
                    }
                )
                if response and response.session and response.user:
                    user_meta = response.user.user_metadata or {}
                    user_obj = AuthUserResponse(
                        id=response.user.id,
                        email=response.user.email or request.email,
                        fullName=user_meta.get("fullName", request.email.split("@")[0]),
                        mobile=user_meta.get("mobile"),
                        organization=user_meta.get("organization"),
                        role=user_meta.get("role", "Network Manager"),
                    )
                    return TokenResponse(
                        access_token=response.session.access_token,
                        user=user_obj,
                    )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password.",
                )
            except Exception as e:
                logger.error(f"Supabase auth login error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password.",
                )

        # Fallback login
        acc = _DEV_ACCOUNTS.get(request.email)
        if not acc or acc["password"] != request.password:
            # Also allow demo login
            if request.email == "demo@example.com" and request.password == "password123":
                return TokenResponse(
                    access_token="demo-jwt-token-12345",
                    user=AuthUserResponse(
                        id="demo-user-1",
                        email="demo@example.com",
                        fullName="Demo Manager",
                        role="Network Manager",
                    ),
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        return TokenResponse(
            access_token=f"dev-token-{acc['id']}",
            user=AuthUserResponse(
                id=acc["id"],
                email=acc["email"],
                fullName=acc["fullName"],
                mobile=acc.get("mobile"),
                organization=acc.get("organization"),
                role=acc["role"],
            ),
        )

    @staticmethod
    def forgot_password(request: ForgotPasswordRequest) -> GenericAuthResponse:
        """
        Triggers Supabase password reset email.
        """
        client = get_supabase_client()
        if client:
            try:
                client.auth.reset_password_email(request.email)
                return GenericAuthResponse(
                    success=True,
                    message="Password reset email has been sent.",
                )
            except Exception as e:
                logger.error(f"Supabase forgot password error: {e}")
                return GenericAuthResponse(
                    success=True,
                    message="If the email exists, a password reset link has been sent.",
                )

        return GenericAuthResponse(
            success=True,
            message="Password reset email simulated in development mode.",
        )

    @staticmethod
    def logout() -> GenericAuthResponse:
        client = get_supabase_client()
        if client:
            try:
                client.auth.sign_out()
            except Exception as e:
                logger.error(f"Supabase sign out error: {e}")
        return GenericAuthResponse(success=True, message="Successfully logged out.")


auth_service = AuthService()
