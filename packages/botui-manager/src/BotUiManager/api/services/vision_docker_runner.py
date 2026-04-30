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
        "docker", "run",# "--rm",
        "--network", network,
        "--name", container_name,
        "-v", f"{parent}:/app/data/",
        botui_image,
        "run-bot", "ocr-test",
        "--image-path", f"/app/data/{Path(image_path).name}"
    ]

    if payload.text_target:
        cmd.extend(["--text-target", payload.text_target])
    
    if payload.search_area:
        search_area_json = json.dumps(payload.search_area.model_dump(), separators=(',', ':'))
        cmd.extend(["--search-area", search_area_json])


    result_process = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        result_cli = json.loads(result_process.stdout)
    except:
        result_cli = {"success": False, "error": result_process.stderr}

    return result_cli, container_name