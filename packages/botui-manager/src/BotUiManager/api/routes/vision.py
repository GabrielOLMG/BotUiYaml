import uuid
import base64
from pathlib import Path
from fastapi import APIRouter
import subprocess

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

    # 1. Executa o container e pega o nome dele
    result_cli, container_name = run_bot_container_vision(job_id, payload)
    
    if not result_cli.get("success"):
        return result_cli

    debug_b64 = None
    try:
        path_inside_container = "/app/data/bbox_texts_debug.png"
        cp_cmd = ["docker", "cp", f"{container_name}:{path_inside_container}", "-"]
        
        # O docker cp com '-' gera um stream TAR
        cp_process = subprocess.run(cp_cmd, capture_output=True)
        
        if cp_process.returncode == 0:
            import tarfile
            import io
            # Extraímos o arquivo do stream TAR em memória
            with tarfile.open(fileobj=io.BytesIO(cp_process.stdout)) as tar:
                # O nome no tar será apenas o nome do arquivo
                member = tar.getmember("bbox_texts_debug.png")
                f = tar.extractfile(member)
                if f:
                    debug_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Erro ao extrair imagem de debug: {e}")
    finally:
        # 3. Agora que pegamos a imagem, podemos remover o container manualmente
        subprocess.run(["docker", "rm", "-f", container_name])

    return {
        "success": True,
        "result": result_cli.get("result"),
        "debug_image": debug_b64
    }