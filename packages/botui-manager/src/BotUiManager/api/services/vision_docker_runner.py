import os
import json
import subprocess


from pathlib import Path


from BotUiManager.api.models import OCRPayload, TemplateMatchPayload


def run_bot_container_vision(
        job_id,
        payload: OCRPayload | TemplateMatchPayload
    )-> dict:
    network = os.getenv("DOCKER_NETWORK", "botui_network")
    container_name = f"botui_vision_{job_id}"
    image_path = payload.image_path
    parent= Path(image_path).parent
    botui_image = os.getenv("BOTUI_IMAGE")

    cmd = [
        "docker", "run", "--rm",
        "--network", network,
        "--name", container_name,
        "-v", f"{parent}:/app/data/", # Mudar para Var Global!
        botui_image, # Mudar para Var Global!
        "run-bot", "ocr-test",
        "--image-path", f"/app/data/{Path(image_path).name}",
        "--text-target", payload.text_target
    ]


    result_process = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:", result_process.stdout)
    print("STDERR:", result_process.stderr)


    
    result_cli = json.loads(result_process.stdout)


    return result_cli