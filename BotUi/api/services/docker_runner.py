import os
import subprocess

from pathlib import Path

from BotUi.api.models import RunBotRequest


def run_bot_container(
        job_id,
        payload: RunBotRequest
    )-> dict:
    container_name = f"botui_{'debug_' if payload.debug else ''}{job_id}"
    dir_name = Path(payload.pipeline_dir).name
    debug_flag = "--debug" if payload.debug else ""


    network = os.getenv("DOCKER_NETWORK", "botui_network")

    init_cmd = ["docker", "run", "-d", "--network", network]
    if not payload.debug:
        init_cmd.append("--rm")
    final_cmd = [
        "--name", container_name,
        "-v", f"{payload.pipeline_dir}:/app/{dir_name}",
        "botui",
        "sh", "-c",
        (   
            f"mkdir -p /app/{dir_name}/outputs/logs && "
            f"run-bot "
            f"--pipeline /app/{dir_name} "
            f"--bot {payload.bot_relative_path} "
            f"--bot-variables {payload.globals_relative_path or ''} "
            f"{debug_flag} "
            f"> /app/{dir_name}/outputs/logs/bot_docker.log 2>&1"
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
        "container_id": result.stdout.strip()
    }