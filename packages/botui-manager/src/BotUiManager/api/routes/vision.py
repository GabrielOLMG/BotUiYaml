import os
import io
import uuid
import json
import base64
import tarfile
import subprocess

from pathlib import Path
from fastapi import APIRouter

from BotUiManager.api.services.general import retrieve_content_from_container
from BotUiManager.api.services.vision_docker_runner import run_container_vision
from BotUiManager.api.models import OCRPayload, TemplateMatchPayload

router = APIRouter()

ROOT_API = os.getenv("VISION_PATH")


@router.post("/vision/template_match", tags=["vision"])
def template_match_simulate(payload: TemplateMatchPayload):
    job_id = str(uuid.uuid4())
    save_path = f"{ROOT_API}/template_match_simulate.png"
    source_image_name = Path(payload.source_image).name 

    docker_code = [
        "-v", f"{payload.source_image}:{ROOT_API}/{source_image_name}"
    ]
    cli_code = [
        "run-bot", "template-match-test", 
        "--save-at", save_path,
        "--source-image", f"{ROOT_API}/{source_image_name}",
    ]
    
    if payload.template_image:
        template_image_name = Path(payload.template_image).name 
        cli_code.extend(["--template-image", f"{ROOT_API}/{template_image_name}"])
        docker_code.extend(["-v", f"{payload.template_image}:{ROOT_API}/{template_image_name}"])

    if payload.search_area:
        search_area_json = json.dumps(payload.search_area.model_dump(), separators=(',', ':'))
        cli_code.extend(["--search-area", search_area_json])

    result_cli, container_name = run_container_vision(
        job_id=job_id, 
        docker_code=docker_code,
        cli_code=cli_code
    )

    subprocess.run(["docker", "rm", "-f", container_name])
    return {
        "success": True,
        "result": result_cli,
        "debug_image": debug_b64

    }

@router.post("/vision/ocr", tags=["vision"])
def ocr_simulate(payload: OCRPayload):
    job_id = str(uuid.uuid4())
    save_path = f"{ROOT_API}/ocr_simulate.png"
    image_path_name = Path(payload.image_path).name 

    docker_code = [
        "-v", f"{payload.image_path}:{ROOT_API}/{image_path_name}"
    ]
    cli_code = [
        "run-bot", "ocr-test",
        "--save-at", save_path,
        "--image-path", f"{ROOT_API}/{image_path_name}",
    ]

    if payload.text_target:
        cli_code.extend(["--text-target", payload.text_target])
    if payload.search_area:
        search_area_json = json.dumps(payload.search_area.model_dump(), separators=(',', ':'))
        cli_code.extend(["--search-area", search_area_json])

    result_cli, container_name = run_container_vision(
        job_id=job_id, 
        docker_code=docker_code,
        cli_code=cli_code
    )

    debug_b64 = retrieve_content_from_container(save_path, container_name, is_binary=True)
    
    subprocess.run(["docker", "rm", "-f", container_name])
    return {
        "success": True,
        "result": result_cli,
        "debug_image": debug_b64
    }
