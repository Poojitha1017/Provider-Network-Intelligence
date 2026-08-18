from fastapi import APIRouter
from app.schemas.simulation import WhatIfRequest, WhatIfResponse
from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/what-if", response_model=WhatIfResponse)
async def run_what_if_simulation(request: WhatIfRequest):
    """
    Executes a non-destructive What-if analysis calculating projected access gap scores,
    provider counts, and risk reductions without altering the database.
    """
    return simulation_service.run_simulation(request)
