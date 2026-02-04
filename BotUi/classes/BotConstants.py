class ScrollConstants:
    MAX_ATTEMPTS = 20
    DISTANCE = 500
    DEFAULT_DIRECTION = "DOWN"


class RetryConstants:
    FIND_RETRY_MAX_ATTEMPTS = 50

# --------------------------------------- #

# TODO: Melhorar se possivel
# TODO: Melhora 1: Tentar fazer check de paths

GLOBAL_FIELDS = {
    "helper": str,
    "wait": (int, float),
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
            "scroll_direction": str,
            "click": bool,
            "y_coord": int,
            "x_coord": int,
            "until_find": str,
            "save_as": str,
            "optional": bool,
            "if_find": str,
            "position": int,
            "side": str,
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
            "save_as": str,
            **GLOBAL_FIELDS
        }
    },
    "DO_WHILE": {
        "required": {
            "while_condition": list,
            "do": list

        },
    },
    "FOR_EACH": {
        "required": {
            "loop_var": str,
            "items": str,
            "steps": list

        },
    }
}


PW_KEYS = {
    # Controle
    "BACKSPACE": "Backspace",
    "TAB": "Tab",
    "ENTER": "Enter",
    "RETURN": "Enter",
    "ESCAPE": "Escape",
    "SPACE": " ",
    "DELETE": "Delete",
    "INSERT": "Insert",

    # Navegação
    "HOME": "Home",
    "END": "End",
    "PAGE_UP": "PageUp",
    "PAGE_DOWN": "PageDown",

    # Setas
    "LEFT": "ArrowLeft",
    "RIGHT": "ArrowRight",
    "UP": "ArrowUp",
    "DOWN": "ArrowDown",

    # Modificadores
    "SHIFT": "Shift",
    "CONTROL": "Control",
    "ALT": "Alt",
    "META": "Meta",
    "COMMAND": "Meta",

    # Funções
    **{f"F{i}": f"F{i}" for i in range(1, 13)},
}


MODIFIER_KEYS = {"SHIFT", "CONTROL", "ALT", "META", "COMMAND"}