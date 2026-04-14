from fastapi import APIRouter
from BotUi.api.services.docker_runner import run_bot_container

router = APIRouter()


@router.post("/jobs/run")
def run_job(payload: dict):
    yaml_path = payload.get("yaml_path")
    data_path = payload.get("data_path")

    result = run_bot_container(yaml_path, data_path)

    return {
        "status": "started",
        **result
    }