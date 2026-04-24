import uuid

from fastapi import APIRouter

from BotUiManager.api.services.vision_docker_runner import run_bot_container_vision
from BotUiManager.api.models import OCRPayload, TemplateMatchPayload, OCRResult

router = APIRouter()

@router.post("/vision/ocr", tags=["vision"])
def ocr_simulate(payload: OCRPayload):
    job_id = str(uuid.uuid4())

    result = run_bot_container_vision(job_id, payload)
    if not result["success"]:
        return result
    
    data = result["result"]
    clean_data = [
        {k: v for k, v in d.items() if k not in ['box', 'score']}
        for d in data
    ]
    result["result"] = clean_data

    return result


@router.post("/vision/template-match", tags=["vision"])
def template_match_simulate(payload: TemplateMatchPayload):
    return {"status": "ok"}