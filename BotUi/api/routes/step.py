from fastapi import APIRouter
from BotUi.api.models import StepPayload

router = APIRouter()

step_updates = {}


@router.post("/step-update")
def update_step(payload: StepPayload):
    step_updates[payload.name] = {**payload.parameters, "debug": payload.debug}
    return {"status": "ok"}

@router.get("/step-update/{step_id}")
def get_step_update(step_id: str):
    if step_id in step_updates:
        data = step_updates.pop(step_id)
        return {"parameters": data, "debug": data["debug"]}

    return {}