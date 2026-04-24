from fastapi import APIRouter
from BotUiManager.api.models import OCRPayload, TemplateMatchPayload

router = APIRouter()

@router.post("/vision/ocr", tags=["vision"])
def ocr_simulate(payload: OCRPayload):
    return {"status": "ok"}


@router.post("/vision/template-match", tags=["vision"])
def template_match_simulate(payload: TemplateMatchPayload):
    return {"status": "ok"}