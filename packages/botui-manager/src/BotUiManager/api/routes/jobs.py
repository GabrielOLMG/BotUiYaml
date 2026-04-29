import uuid
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response

from BotUiManager.api.models import RunBotRequest, RunBotResponse
from BotUiManager.api.services.bot_docker_runner import run_bot_container, get_container_logs

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


@router.get("/jobs/{job_id}/logs", tags=["jobs"])
def get_job_logs(job_id: str):
    container_name = f"botui_{job_id}" 
    
    logs = get_container_logs(container_name)
    
    return {
        "job_id": job_id,
        "logs": logs
    }


@router.get("/jobs/{job_id}/screenshot", tags=["jobs"])
def get_job_screenshot(job_id: str, pipeline_dir: str):
    container_name = f"botui_{job_id}"
    dir_name = Path(pipeline_dir).name
    screenshot_path = f"/app/bots/{dir_name}/outputs/screenshots/screenshot_page.png"

    try:
        # Usamos 'cat' dentro do container para jogar os bytes no stdout do processo
        cmd = ["docker", "exec", container_name, "cat", screenshot_path]
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode != 0:
            # Se o arquivo ainda não existe (o bot não tirou print ainda)
            raise HTTPException(status_code=404, detail="Screenshot ainda não gerada.")

        # Enviamos os bytes capturados no stdout diretamente para o frontend
        return Response(content=result.stdout, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))