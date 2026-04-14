import subprocess
import uuid


def run_bot_container(bot_folder_path: str):
    job_id = str(uuid.uuid4())

    container_name = f"botui_{job_id}"
    import os
    print(os.listdir())
    cmd = [
        "docker", "run", "-d", "--rm",
        "--name", container_name,
        "-v", "/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/BotUi_Examples:/app/BotUi_Examples",
        "botui", 
        "python", "BotUi_Examples/run.py"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr)

    return {
        "job_id": job_id,
        "container_name": container_name,
        "container_id": result.stdout.strip()
    }