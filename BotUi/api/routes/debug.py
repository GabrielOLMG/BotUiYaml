from pydantic import BaseModel

from fastapi import APIRouter
import threading

router = APIRouter()

# =========================
# Estado global (MVP)
# =========================
class DebugState:
    def __init__(self):
        self.paused = False
        self.action = "continue"

state = DebugState()

# =========================
# PAUSE
# =========================
@router.post("/pause")
def pause():
    state.paused = True
    return {"status": "paused"}


# =========================
# RESUME 
# =========================

class ResumeRequest(BaseModel):
    action: str  # "continue" | "stop"


@router.post("/resume")
def resume(req: ResumeRequest):
    state.paused = False
    state.action = req.action
    return {"status": "ok", "action_received": req.action}


# =========================
# STATUS
# =========================
@router.get("/status")
def status():
    return {
        "paused": state.paused,
        "action": state.action
    }