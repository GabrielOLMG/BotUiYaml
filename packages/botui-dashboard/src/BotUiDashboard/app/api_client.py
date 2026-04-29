import requests

API_BASE_URL = "http://botui_api:8000"

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