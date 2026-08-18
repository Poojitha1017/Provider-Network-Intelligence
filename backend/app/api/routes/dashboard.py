from fastapi import APIRouter
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.decision_service import decision_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary():
    """
    Returns dynamically computed network overview statistics, access gap distribution,
    specialty shortages, trend line, and top critical areas.
    """
    return decision_service.get_dashboard_summary()
