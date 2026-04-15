import subprocess

from pathlib import Path

from BotUi.api.models import RunBotRequest


def run_bot_container(
        job_id,
        payload: RunBotRequest
    )-> dict:
    container_name = f"botui_{job_id}"
    dir_name = Path(payload.pipeline_dir).name
     
    cmd = [
        "docker", "run", "-d", "--rm",
        "--name", container_name,
        "-v", f"{payload.pipeline_dir}:/app/{dir_name}",
        "botui", 
        "python", f"{dir_name}/run.py" # TODO: Criar CLI para trocar isto!
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr)

    return {
        "job_id": job_id,
        "container_name": container_name,
        "container_id": result.stdout.strip()
    }