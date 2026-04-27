import uuid

from fastapi import APIRouter

from BotUiManager.api.services.vision_docker_runner import run_bot_container_vision
from BotUiManager.api.models import OCRPayload, TemplateMatchPayload, OCRResult

router = APIRouter()

def remove_box_from_output(data: dict) -> dict:
    import copy
    data = copy.deepcopy(data)

    debug_json = data.get("result", {}).get("debug_json", {})

    for region, items in debug_json.items():
        for item in items:
            item.pop("box", None)  # remove "box" se existir
            item.pop("score", None)  # remove "box" se existir
            item.pop("center", None)  # remove "box" se existir


    return data


@router.post("/vision/ocr", tags=["vision"])
def ocr_simulate(payload: OCRPayload):
    job_id = str(uuid.uuid4())

    result = run_bot_container_vision(job_id, payload)
    if not result["success"]:
        return result
    
    result = remove_box_from_output(result)
    
    return result


@router.post("/vision/template-match", tags=["vision"])
def template_match_simulate(payload: TemplateMatchPayload):
    return {"status": "ok"}