class ScrollConstants:
    MAX_ATTEMPTS = 50
    DISTANCE = 500
    DEFAULT_DIRECTION = "DOWN"


class RetryConstants:
    FIND_RETRY_MAX_ATTEMPTS = 50

# --------------------------------------- #

# TODO: Melhorar se possivel
# TODO: Melhora 1: Tentar fazer check de paths

GLOBAL_FIELDS = {
    "helper": str,
    "wait": float,
    "debug": bool
}

ACTION_SCHEMA = {
    "FIND": {
        "required": {
            "object_type": str,
        },
        "optional": {
            "in_text": bool,
            "text": str,
            "image_path": str,
            "scroll": bool,
            "scroll_image_path": str,
            "click": bool,
            "y_coord": int,
            "x_coord": int,
            "until_find": str,
            "save_as": str,
            "optional": bool,
            "if_find": str,
            **GLOBAL_FIELDS
        },
    },
    "KEYS_SELECTIONS": {
        "required": {
            "keys": list,
        },
        "optional": {
            **GLOBAL_FIELDS
        }
    },
    "WRITE": {
        "required_one_of": {
            "text": str,
            "file_path": str
        },
        "optional": {
            **GLOBAL_FIELDS
        }
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
        "optional": {
            **GLOBAL_FIELDS
        }
    },
    "DO_WHILE": {
        "required": {
            "while_condition": list,
            "do": list

        },
    }
}

