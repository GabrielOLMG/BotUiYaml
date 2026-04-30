import base64
import requests

API_BASE_URL = "http://botui_api:8000"

def get_outputs(container_id, pipeline_name):
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{container_id}/{pipeline_name}/collect", timeout=5)
        if not response.status_code == 200:
            return False, None, "Offline", None
        
        data = response.json()
        exists =  data.get("exists", False) 
        logs = response.json().get("logs", "Sem logs.") 
        screenshot_b64 =  data.get("screenshot") 
        debug_screenshot_b64 =  data.get("debug_screenshot") 

        
        screenshot = None
        if screenshot_b64:
            screenshot = base64.b64decode(screenshot_b64)
        
        screenshot_debug = None
        if debug_screenshot_b64:
            screenshot_debug = base64.b64decode(debug_screenshot_b64)

        return exists, screenshot, logs, screenshot_debug
    except Exception as e:
        return False, None, f"Erro de conexão: {str(e)}", None

def ocr_endpoint(payload):
    result = {
        "success": False,
        "message": None,
        "json": None,
        "image": None
    }
    try:
        response = requests.post(f"{API_BASE_URL}/vision/ocr", json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            result["success"] = True
            result["message"] = "Analysis finished!"

            result["json"] = data.get("result")

            if data.get("debug_image"):
                result["image"] = base64.b64decode(data["debug_image"])
        else:
            result["message"] = f"Api Error: {response.text}"
        
        return result
    except Exception as err:
        result["message"] = f"Error: {str(err)}"
        return result




        
    


def start_bot_api(payload):
    return requests.post(f"{API_BASE_URL}/jobs/run", json=payload, timeout=10)