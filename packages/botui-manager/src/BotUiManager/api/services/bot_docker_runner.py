import os
import subprocess

from pathlib import Path

from BotUiManager.api.models import RunBotRequest

ROOT_API = os.getenv("BOT_PATH")
NETWORK = os.getenv("DOCKER_NETWORK", "botui_network")

def run_bot_container(
        job_id,
        payload: RunBotRequest,
    )-> dict:
    container_name = f"botui_{'debug_' if payload.debug else ''}{job_id}"
    dir_name = Path(payload.pipeline_dir).name
    debug_flag = "--debug" if payload.debug else ""

    

    init_cmd = ["docker", "run", "-d", "--network", NETWORK]
    if not payload.debug:
        init_cmd.append("--rm")
    final_cmd = [
        "--name", container_name,
        "-v", f"{payload.pipeline_dir}:{ROOT_API}/{dir_name}",
        "botui",
        "sh", "-c",
        (   
            f"mkdir -p {ROOT_API}/{dir_name}/outputs/logs && "
            f"run-bot start-bot "
            f"--pipeline {ROOT_API}/{dir_name} "
            f"--bot {payload.bot_relative_path} "
            f"--bot-variables {payload.globals_relative_path or ''} "
            f"{debug_flag} "
            f"2>&1 | tee {ROOT_API}/{dir_name}/outputs/logs/bot_docker.log"
        )
    ]
    cmd = init_cmd + final_cmd
    print(cmd)
    

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr)

    return {
        "job_id": job_id,
        "container_name": container_name,
        "container_id": result.stdout.strip(),
        "pipeline_name": dir_name
    }


def get_container_logs(container_name: str):
    try:
        cmd = ["docker", "logs", "--tail", "50", container_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"Container {container_name} não encontrado ou já finalizado."
            
        return result.stdout
    except Exception as e:
        return f"Erro ao acessar Docker: {str(e)}"