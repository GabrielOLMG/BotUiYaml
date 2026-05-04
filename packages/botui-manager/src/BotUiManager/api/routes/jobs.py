import os
import json
import uuid
import base64
import subprocess
from fastapi import APIRouter, HTTPException, Response, status

from BotUiManager.api.models import RunBotRequest, RunBotResponse
from BotUiManager.api.services.bot_docker_runner import run_bot_container, get_container_logs

router = APIRouter()

ROOT_API = os.getenv("BOT_PATH")

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


@router.get("/jobs/{container_id}/kill", tags=["jobs"])
def kill_bot(container_id: str):
    try:
        subprocess.run(
            ["docker", "rm", "-f", container_id],
            check=True,
            capture_output=True,
            text=True
        )
        
        return {
            "status": "success",
            "message": f"Container {container_id} stopped and removed via CLI."
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip()
        if "No such container" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Container {container_id} not found in Docker."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Docker CLI error: {error_msg}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
 

@router.get("/jobs/{container_id}/{pipeline_name}/collect", tags=["jobs"])
def collect_container_outputs(container_id: str, pipeline_name: str):
    from BotUiManager.api.services.general import retrieve_folder_from_container, retrieve_logs_from_container, container_exists
    outputs_path = f"{ROOT_API}/{pipeline_name}/outputs"


    screenshot_path = f"./screenshots/screenshot_page.png" 
    debug_screenshot_path = f"./debugs/debug.png" 
    debug_json_path = f"./debugs/debug.json"


    result = {
        "exists": False,
        "screenshot": None,
        "debug_screenshot": None,
        "debug_json": None,
        "logs": None
    }
    if not container_exists(container_id):
            return result
    
    result["exists"] = True
    result["logs"] = retrieve_logs_from_container(container_id)
    files = retrieve_folder_from_container(container_id, outputs_path)

    if files:
        if screenshot_path in files:
            result["screenshot"] = base64.b64encode(files[screenshot_path]).decode("utf-8")
        
        if debug_screenshot_path in files:
            result["debug_screenshot"] = base64.b64encode(files[debug_screenshot_path]).decode("utf-8")
        if debug_json_path in files:
            try:
                result["debug_json"] = json.loads(files[debug_json_path].decode("utf-8"))
            except:
                pass

    return result
    
