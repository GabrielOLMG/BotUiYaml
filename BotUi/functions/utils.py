import os
import re
import subprocess
import hashlib
from ruamel.yaml import YAML

def open_yaml(path):
    yaml = YAML(typ="safe")
    yaml.allow_duplicate_keys = True

    with open(path, "r") as f:
        data = yaml.load(f)
    return data

def open_file(path):
    """Abre um arquivo de texto (YAML, TXT, MD etc.) e retorna o conteúdo como string."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content

def resolve_variables(value, data_store, ignore_miss=True):
    """
    Substitui ocorrências de $VAR em strings por valores do data_store.
    Exemplo:
        "Bearer $TOKEN" -> "Bearer abc123"
    """
    if not isinstance(value, str):
        return value

    pattern = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")

    def replacer(match):
        var_name = match.group(1)
        if var_name not in data_store:
            if ignore_miss:
                return f"${var_name}" # Volta para o valor orignal!
            else:
                raise ValueError(f"Variable ${var_name} not found in data_store")
        return str(data_store[var_name])

    return pattern.sub(replacer, value)

def evaluate_condition(condition_str: str) -> bool:
    try:
        allowed_builtins = {
            "True": True,
            "False": False,
            "None": None,
            "str": str,
            "len": len,
            "bool": bool,
        }
        result = bool(eval(condition_str, {"__builtins__": allowed_builtins}, {}))
        return True, None, result
    except Exception as e:
        return False, f"Erro ao avaliar condição '{condition_str}': {e}", None

def run_script(script_path, flags):
    try:
        # Monta a lista de argumentos
        cmd = ["bash", script_path]
        if flags:
            # Divide em múltiplos argumentos se houver espaços
            if isinstance(flags, str):
                cmd.extend(flags.split())
            elif isinstance(flags, list):
                cmd.extend(flags)

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        return True, None, output

    except subprocess.CalledProcessError as e:
        return False, f"Script {script_path} failed:\n{e.stderr}", None

def hash_from_bytes(data: bytes) -> str:
    return hashlib.sha256(data).digest()

def parse_coord(coord):
    if coord is None:
        return None

    if isinstance(coord, str):
        try:
            coord = coord.strip("[]")
            x, y = coord.split(",")
            coord = [float(x), float(y)]
        except Exception:
            return None

    if (
        isinstance(coord, (list, tuple))
        and len(coord) == 2
        and all(isinstance(v, (int, float)) for v in coord)
    ):
        return coord

    return None

def check_path(path: str) -> bool:
    return os.path.exists(path)