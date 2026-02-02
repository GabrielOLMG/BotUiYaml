from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

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

def send_key_sequence(page, sequence):
    """
    Envia uma sequência de teclas no Playwright.
    Ex:
        send_key_sequence(page, ["CONTROL", "a"])
        send_key_sequence(page, ["SHIFT", "TAB"])
        send_key_sequence(page, ["SPACE", "BACKSPACE"])
    """
    try: 
        pressed_modifiers = []

        for item in sequence:
            key = item.upper()

            # Modificadores
            if key in MODIFIER_KEYS:
                pw_key = PW_KEYS[key]
                page.keyboard.down(pw_key)
                pressed_modifiers.append(pw_key)

            # Teclas especiais
            elif key in PW_KEYS:
                pw_key = PW_KEYS[key]

                # Espaço real
                if pw_key == " ":
                    page.keyboard.type(" ")
                else:
                    page.keyboard.press(pw_key)

            # Texto normal
            else:
                page.keyboard.type(item)

        # Solta modificadores no final
        for mod in reversed(pressed_modifiers):
            page.keyboard.up(mod)
        return True, None
    except Exception as e:
        return False, e