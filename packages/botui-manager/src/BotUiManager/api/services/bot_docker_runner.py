import os
import subprocess

from pathlib import Path

from BotUiManager.api.models import RunBotRequest

ROOT_API = os.getenv("BOT_PATH")
NETWORK = os.getenv("DOCKER_NETWORK", "botui_network")
BOTUI_WORKER_NAME = os.getenv("BOTUI_WORKER_NAME")

def run_bot_container(
        job_id, 
        payload: RunBotRequest,
    ) -> dict:
    container_name = f"{BOTUI_WORKER_NAME}_{job_id}"
    
    container_pipeline_path = f"{ROOT_API}/{job_id}"
    output_folder_name = f"outputs_{job_id}" 
    full_output_path = f"{container_pipeline_path}/{output_folder_name}"

    # 2. Comando Docker
    init_cmd = ["docker", "run", "-d", "--network", NETWORK]
    
    final_cmd = [
        "--name", container_name,
        "-v", f"{payload.pipeline_dir}:{container_pipeline_path}",
        "botui",
        "run-bot", "start-bot",
        "--pipeline", container_pipeline_path,
        "--bot", payload.bot_relative_path,
        "--bot-variables", payload.globals_relative_path or '',
        "--output-folder", full_output_path 
    ]

    cmd = init_cmd + final_cmd

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Docker Error: {result.stderr}")

    return {
        "job_id": job_id,
        "container_name": container_name,
        "container_id": result.stdout.strip(),
    }