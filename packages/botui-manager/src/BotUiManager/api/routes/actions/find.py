from fastapi import APIRouter
from BotUiManager.api.models import FindRequest

router = APIRouter()

@router.post("/find/simulate", tags=["actions"])
def find_simulate(payload: FindRequest):
    return {"status": "ok"}