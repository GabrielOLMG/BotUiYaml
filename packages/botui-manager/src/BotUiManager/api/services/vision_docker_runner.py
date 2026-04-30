import os
import json
import subprocess

NETWORK = os.getenv("DOCKER_NETWORK", "botui_network")
IMAGE = os.getenv("BOTUI_IMAGE")


def run_container_vision(
        job_id,
        docker_code: list,
        cli_code: list
) -> dict:
    container_name = f"botui_vision_{job_id}"

    cmd = [
        "docker", "run",
        "--network", NETWORK,
        "--name", container_name,
        *docker_code,
        IMAGE,
        *cli_code
    ]

    result_process = subprocess.run(cmd, capture_output=True, text=True)

    try:
        result_cli = json.loads(result_process.stdout)
    except:
        result_cli = {"success": False, "error": result_process.stderr}

    return result_cli, container_name
