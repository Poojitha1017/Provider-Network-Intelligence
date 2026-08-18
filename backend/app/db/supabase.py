import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Supabase is disabled. Operating exclusively in local CSV fallback mode.
    """
    return None


def get_supabase_admin_client() -> Optional[Client]:
    """
    Supabase is disabled. Operating exclusively in local CSV fallback mode.
    """
    return None


def is_supabase_connected() -> bool:
    """
    Checks if Supabase credentials are configured and reachable.
    """
    return False
