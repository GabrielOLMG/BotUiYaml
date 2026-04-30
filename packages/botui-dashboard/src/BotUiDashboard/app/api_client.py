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

def fetch_logs(job_id):
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/logs", timeout=2)
        return response.json().get("logs", "Sem logs.") if response.status_code == 200 else "Offline"
    except: return "Erro de conexão"

def fetch_screenshot(job_id, pipeline_dir):
    try:
        params = {"pipeline_dir": pipeline_dir}
        res = requests.get(f"{API_BASE_URL}/jobs/{job_id}/screenshot", params=params, timeout=2)
        return res.content if res.status_code == 200 else None
    except: return None

def start_bot_api(payload):
    return requests.post(f"{API_BASE_URL}/jobs/run", json=payload, timeout=10)