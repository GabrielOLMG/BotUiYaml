import io
import base64
import tarfile
import subprocess

def container_exists(container_id):
    """
    True-> Exists
    """
    try:
        result = subprocess.run(["docker", "inspect", container_id],capture_output=True,text=True)
        return result.returncode == 0
    except Exception:
        return False

def retrieve_folder_from_container(container_id, container_path):
    artifacts = {}
    try:
        cmd = ["docker", "cp", f"{container_id}:{container_path}/.", "-"]
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            with tarfile.open(fileobj=io.BytesIO(result.stdout)) as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        f = tar.extractfile(member)
                        if f:
                            artifacts[member.name] = f.read()
    except Exception as e:
        print(f"Erro ao extrair: {e}")
    return artifacts
    
    return artifacts

def retrieve_content_from_container(path, container_id, is_binary=True):
    try:
        cmd = ["docker", "cp", f"{container_id}:{path}", "-"]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            return None
        
        with tarfile.open(fileobj=io.BytesIO(result.stdout)) as tar:
            filename = path.split("/")[-1]
            f = tar.extractfile(filename)
            if f:
                content = f.read()
                if is_binary:
                    return base64.b64encode(content).decode("utf-8")
                return content.decode("utf-8")

        return None
    except Exception:
        return None

def retrieve_logs_from_container(container_id):
    try:
        cmd = ["docker", "logs", "--tail", "100", container_id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else None
    except Exception:
        return None