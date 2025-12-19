import os
from typing import Optional, List, Dict, Literal, Any
from pydantic import BaseModel, model_validator, field_validator, RootModel

from typing import Type

GLOBAL_FIELDS = {
    "helper": str,
    "wait": float,
}

ACTION_SCHEMA = {
    "FIND": {
        "required": {
            "object_type": str,
        },
        "optional": {
            "text": str,
            "image_path": str,
            "scroll": bool,
            "scroll_image_path": str,
            "click": bool,
            "y_coord": int,
            "x_coord": int,
            "until_find": str,
            "save_as": str,
            **GLOBAL_FIELDS
        },
    },
    "KEYS_SELECTIONS": {
        "required": {
            "keys": list,
        },
    },
    "WRITE": {
        "required_one_of": {
            "text": str,
            "file_path": str
        },
    },
    "RUN_SCRIPT": {
        "required": {
            "script_path": str,
        },
        "optional": {
            **GLOBAL_FIELDS
        }
    },
    "UPLOAD_FILE": {
        "required": {
            "file_path": str,
            "coord": (list, str),  # aceita os dois por agora
        },
        "optional": {
            **GLOBAL_FIELDS
        }
    },
    "STOP_IF": {
        "required": {
            "condition": str,
        },
    },
    "FIND_TEXT_BY_COLOR": {
        "required": {
            "color": str,
        },
    },
}


# ============================================================
# CONFIGURAÇÃO GLOBAL OPCIONAL
# ============================================================

class GlobalConfig(BaseModel):
    """Bloco opcional de configuração global."""
    variables: Optional[Dict[str, Any]] = None  # Ex: {"base_path": "/home/user", "lang": "pt"}


# ============================================================
# STEP E PIPELINE (seu código original)
# ============================================================

class Step(BaseModel):
    action: str

    model_config = {
        "extra": "allow"  # permite campos dinâmicos
    }

    @model_validator(mode="after")
    def validate_by_schema(self):
        action = self.action

        if action not in ACTION_SCHEMA:
            raise ValueError(f"Action inválida: {action}")

        schema = ACTION_SCHEMA[action]

        required = schema.get("required", {})
        optional = schema.get("optional", {})
        one_of = schema.get("required_one_of", {})

        allowed_fields = {"action"} | set(required) | set(optional) | set(one_of)

        # 🔒 Bloqueia campos não permitidos
        extra_fields = set(self.model_extra or {}) - allowed_fields
        if extra_fields:
            raise ValueError(
                f"[{action}] campos não permitidos: {extra_fields}"
            )

        # ✅ required (todos)
        for field, expected in required.items():
            value = getattr(self, field, None)
            if value is None:
                raise ValueError(f"[{action}] campo obrigatório '{field}' ausente")
            if not isinstance(value, expected):
                raise ValueError(
                    f"[{action}] '{field}' deve ser {expected}, recebido {type(value)}"
                )

        # ✅ one_of (pelo menos um)
        if one_of:
            present = []
            for field, expected in one_of.items():
                value = getattr(self, field, None)
                if value is not None:
                    if not isinstance(value, expected):
                        raise ValueError(
                            f"[{action}] '{field}' deve ser {expected}, recebido {type(value)}"
                        )
                    present.append(field)

            if not present:
                raise ValueError(
                    f"[{action}] requer um dos campos: {list(one_of.keys())}"
                )

        # ✅ optional (tipo)
        for field, expected in optional.items():
            value = getattr(self, field, None)
            if value is not None and not isinstance(value, expected):
                raise ValueError(
                    f"[{action}] '{field}' deve ser {expected}, recebido {type(value)}"
                )

        return self




class Pipeline(BaseModel):
    url: Optional[str] = None
    steps: List[Step]

    @field_validator("steps")
    @classmethod
    def validate_steps_not_empty(cls, v):
        if not v:
            raise ValueError("Cada pipeline deve conter pelo menos um passo")
        return v


# ============================================================
# MODELO FINAL QUE UNE CONFIG + PIPELINES
# ============================================================

class PipelineConfig(BaseModel):
    """Modelo raiz que suporta config + pipelines."""
    config: Optional[GlobalConfig] = None
    pipelines: Dict[str, Pipeline]

    @model_validator(mode="after")
    def validate_unique_pipeline_names(self):
        data = self.pipelines
        if len(data) != len(set(data.keys())):
            raise ValueError("Nomes de pipelines duplicados detectados")
        return self
