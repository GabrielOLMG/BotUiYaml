from fastapi import APIRouter


from BotUi.api.models import RunBotRequest
from BotUi.api.services.docker_runner import run_bot_container

router = APIRouter()


@router.post("/jobs/run")
def run_job(payload: dict):
    bot_folder_path = payload.get("bot_path", "BotUi_Examples")
    print("bot_folder_path")
    result = run_bot_container(bot_folder_path)

    return {
        "status": "started",
        **result
    }
