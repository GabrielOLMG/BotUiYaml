class ScrollConstants:
    MAX_ATTEMPTS = 20
    DISTANCE = 500
    DEFAULT_DIRECTION = "DOWN"

# --------------------------------------- #

# TODO: Melhorar se possivel
# TODO: Melhora 1: Tentar fazer check de paths

GLOBAL_FIELDS = {
    "helper": str,
    "save_url": str,
    "wait": (int, float),
    "debug": bool,
    "refresh": bool
}

ACTION_SCHEMA = {
    "FIND": {
        "required": {
            "object_type": str,
        },
        "required_one_of": {
            "text": str,
            "image_path": str,

        },
        "optional": {
            "in_text": bool, # TODO: Pode fazer parte do operator!

            # TODO: Transformar em um dicionario relacionado ao scrol?
            "scroll": bool,
            "scroll_direction": str,
            # ---------------

            "next": dict, # Como validar melhor?

            "y_coord": int,
            "x_coord": int,
            "save_as": str,
            "click": bool,

            # TODO: Transformar em um diconario q englobe os 2?
            "position": int,
            "side": str,
            # ---------------
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