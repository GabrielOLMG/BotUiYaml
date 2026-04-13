from pydantic import BaseModel

from fastapi import APIRouter
import threading

router = APIRouter()

# =========================
# Estado global (MVP)
# =========================
class DebugState:
    def __init__(self):
        self.event = threading.Event()
        self.action = None  # "continue" | "stop"

state = DebugState()


# =========================
# Health check
# =========================
@router.get("/")
def root():
    return {"status": "debug server running"}


# =========================
# PAUSE (bot bloqueia aqui)
# =========================
@router.post("/pause")
def pause():
    """
    Bot chama isso e fica bloqueado até /resume
    """
    state.event.clear()
    state.event.wait() 

    return {"status": "resumed", "action": state.action}


# =========================
# RESUME (frontend libera bot)
# =========================

class ResumeRequest(BaseModel):
    action: str  # "continue" | "stop"


@router.post("/resume")
def resume(req: ResumeRequest):
    """
    Frontend decide o que fazer
    """
    state.action = req.action
    state.event.set()

    return {
        "status": "ok",
        "action_received": req.action
    }