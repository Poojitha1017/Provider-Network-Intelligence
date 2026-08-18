import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.supabase import get_supabase_client
from app.services.auth_service import _DEV_ACCOUNTS

logger = logging.getLogger("uvicorn.error")
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Extracts and verifies the user session from the Bearer token using Supabase Auth.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    client = get_supabase_client()

    if client:
        try:
            user_response = client.auth.get_user(token)
            if user_response and user_response.user:
                user = user_response.user
                return {
                    "id": user.id,
                    "email": user.email,
                    "role": user.user_metadata.get("role", "Network Manager") if user.user_metadata else "Network Manager",
                    "fullName": user.user_metadata.get("fullName", user.email) if user.user_metadata else user.email,
                    "user_metadata": user.user_metadata or {},
                }
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # In development mode without active Supabase credentials
    # Check if token matches a registered dev account
    for email, acc in _DEV_ACCOUNTS.items():
        if f"dev-token-{acc['id']}" == token:
            return {
                "id": acc["id"],
                "email": acc["email"],
                "role": acc["role"],
                "fullName": acc["fullName"],
                "user_metadata": {"organization": acc.get("organization"), "mobile": acc.get("mobile")},
            }

    return {
        "id": "dev-user-id",
        "email": "testuser@example.com",
        "role": "Network Manager",
        "fullName": "Test User",
        "user_metadata": {},
    }
