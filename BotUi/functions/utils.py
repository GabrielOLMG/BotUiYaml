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

import re

def resolve_variables(value, data_store):
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
        result = eval(condition_str, {"__builtins__": allowed_builtins}, {})
        return bool(result)
    except Exception as e:
        print(f"❌ Erro ao avaliar condição '{condition_str}': {e}")
        return False

