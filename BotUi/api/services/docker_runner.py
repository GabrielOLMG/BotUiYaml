import subprocess
import uuid


def run_bot_container(yaml_path: str, data_path: str):
    job_id = str(uuid.uuid4())

    container_name = f"botui_{job_id}"

    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "-v", f"{data_path}:/app/data",
        "-v", f"{yaml_path}:/app/yaml",
        "botui-image", 
        "python", "run.py"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr)

    return {
        "job_id": job_id,
        "container_name": container_name,
        "container_id": result.stdout.strip()
    }