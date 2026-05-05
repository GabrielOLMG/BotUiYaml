import os
import re
import json
import uuid
import base64
import subprocess
from fastapi import APIRouter, HTTPException, Response, status, BackgroundTasks

from BotUiManager.api.models import RunBotRequest, RunBotResponse
from BotUiManager.api.services.bot_docker_runner import run_bot_container
from BotUiManager.api.services.general import retrieve_folder_from_container, retrieve_logs_from_container, container_exists

router = APIRouter()

ROOT_API = os.getenv("BOT_PATH")
BOTUI_WORKER_NAME = os.getenv("BOTUI_WORKER_NAME")


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


@router.post("/jobs/batch", tags=["jobs"])
def run_batch_jobs(payload: RunBotRequest, background_tasks: BackgroundTasks):
    """
    Inicia N instâncias do mesmo bot em paralelo.
    """
    n_instances = payload.n_instances
    def start_multiple_bots(p: RunBotRequest, count: int):
        for i in range(count):
            job_id = str(uuid.uuid4())
            try:
                run_bot_container(job_id, p)
                print(f"Bot {i+1}/{count} iniciado com sucesso.")
            except Exception as e:
                print(f"Falha ao iniciar bot {i+1}: {e}")

    background_tasks.add_task(start_multiple_bots, payload, n_instances)

    return {
        "status": "batch_started",
        "total_requested": n_instances,
        "message": f"Iniciando {n_instances} instâncias em segundo plano."
    }


@router.get("/jobs/{job_id}/kill", tags=["jobs"])
def kill_bot(job_id: str):
    try:
        container_name = f"{BOTUI_WORKER_NAME}_{job_id}"

        subprocess.run(
            ["docker", "rm", "-f", container_name],
            check=True,
            capture_output=True,
            text=True
        )
        
        return {
            "status": "success",
            "message": f"Container {container_name} stopped and removed via CLI."
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip()
        if "No such container" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Container {container_name} not found in Docker."
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
 

@router.get("/jobs/{job_id}/collect", tags=["jobs"])
def collect_container_outputs(job_id: str):
    outputs_path = f"{ROOT_API}/{job_id}/outputs_{job_id}"
    container_name = f"{BOTUI_WORKER_NAME}_{job_id}"

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
    if not container_exists(container_name):
            return result
    
    result["exists"] = True
    result["logs"] = retrieve_logs_from_container(container_name)
    files = retrieve_folder_from_container(container_name, outputs_path)

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
    
@router.get("/jobs/all", tags=["jobs"])
def get_active_jobs():
    try:
        cmd = [
            "docker", "ps", "-a", 
            "--filter", "name=botui_worker_", 
            "--format", '{"id": "{{.ID}}", "name": "{{.Names}}", "status": "{{.Status}}", "state": "{{.State}}"}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Erro no comando Docker: {result.stderr}")
            return []

        if not result.stdout.strip():
            return []

        lines = result.stdout.strip().split('\n')
        containers = []
        
        for line in lines:
            try:
                data = json.loads(line)
                
                exit_code = 0
                if data["state"] == "exited":
                    match = re.search(r'\((\d+)\)', data["status"])
                    if match:
                        exit_code = int(match.group(1))
                
                data["exit_code"] = exit_code
                containers.append(data)
            except (json.JSONDecodeError, ValueError):
                continue
        
        return containers

    except Exception as e:
        print(f"Erro ao listar containers: {e}")
        return []