import uuid

from fastapi import APIRouter


from BotUiManager.api.models import RunBotRequest, RunBotResponse
from BotUiManager.api.services.docker_runner import run_bot_container

router = APIRouter()


@router.post(
    path="/jobs/run",
    response_model=RunBotResponse,
    tags=["jobs"]
)
def run_job(payload: RunBotRequest):
    job_id = str(uuid.uuid4())

    result = run_bot_container(
        job_id =job_id,
        payload=payload,
    )


    return RunBotResponse(
        status="STARTED",
        **result
    )
