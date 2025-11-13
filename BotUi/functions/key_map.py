from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

keys = {
    # Controle e navegação
    "NULL": Keys.NULL,
    "CANCEL": Keys.CANCEL,
    "HELP": Keys.HELP,
    "BACKSPACE": Keys.BACKSPACE,
    "TAB": Keys.TAB,
    "CLEAR": Keys.CLEAR,
    "RETURN": Keys.RETURN,
    "ENTER": Keys.ENTER,
    "SHIFT": Keys.SHIFT,
    "CONTROL": Keys.CONTROL,
    "ALT": Keys.ALT,
    "PAUSE": Keys.PAUSE,
    "ESCAPE": Keys.ESCAPE,
    "SPACE": Keys.SPACE,
    "PAGE_UP": Keys.PAGE_UP,
    "PAGE_DOWN": Keys.PAGE_DOWN,
    "END": Keys.END,
    "HOME": Keys.HOME,
    "LEFT": Keys.LEFT,
    "UP": Keys.UP,
    "RIGHT": Keys.RIGHT,
    "DOWN": Keys.DOWN,
    "INSERT": Keys.INSERT,
    "DELETE": Keys.DELETE,

    # Teclas de função
    "F1": Keys.F1,
    "F2": Keys.F2,
    "F3": Keys.F3,
    "F4": Keys.F4,
    "F5": Keys.F5,
    "F6": Keys.F6,
    "F7": Keys.F7,
    "F8": Keys.F8,
    "F9": Keys.F9,
    "F10": Keys.F10,
    "F11": Keys.F11,
    "F12": Keys.F12,

    # Modificadores do keypad e teclas especiais
    "COMMAND": Keys.COMMAND,
    "META": Keys.META,

    # Teclado numérico e símbolos especiais
    "NUMPAD0": Keys.NUMPAD0,
    "NUMPAD1": Keys.NUMPAD1,
    "NUMPAD2": Keys.NUMPAD2,
    "NUMPAD3": Keys.NUMPAD3,
    "NUMPAD4": Keys.NUMPAD4,
    "NUMPAD5": Keys.NUMPAD5,
    "NUMPAD6": Keys.NUMPAD6,
    "NUMPAD7": Keys.NUMPAD7,
    "NUMPAD8": Keys.NUMPAD8,
    "NUMPAD9": Keys.NUMPAD9,
    "MULTIPLY": Keys.MULTIPLY,
    "ADD": Keys.ADD,
    "SEPARATOR": Keys.SEPARATOR,
    "SUBTRACT": Keys.SUBTRACT,
    "DECIMAL": Keys.DECIMAL,
    "DIVIDE": Keys.DIVIDE,

    # Setas e navegação avançada
    "ARROW_LEFT": Keys.ARROW_LEFT,
    "ARROW_UP": Keys.ARROW_UP,
    "ARROW_RIGHT": Keys.ARROW_RIGHT,
    "ARROW_DOWN": Keys.ARROW_DOWN,

    # Diversos
    "SEMICOLON": Keys.SEMICOLON,
    "EQUALS": Keys.EQUALS,
}


modifier_keys = {"CONTROL", "SHIFT", "ALT", "COMMAND", "META"}

def send_key_sequence(driver, sequence):
    """
    Recebe uma lista de teclas e envia na sequência.
    Exemplo:
        send_key_sequence(driver, ["CONTROL", "a"])
        send_key_sequence(driver, ["SPACE", "BACKSPACE"])
    """
    actions = ActionChains(driver)
    pressed_modifiers = []

    for item in sequence:
        upper_item = item.upper()

        if upper_item in modifier_keys:
            actions.key_down(keys[upper_item])
            pressed_modifiers.append(keys[upper_item])
        elif upper_item == "SPACE":
            # Força um espaço real em vez de Keys.SPACE
            actions.send_keys(" ")
        elif upper_item in keys:
            # Tecla especial, mas não modificadora → envia diretamente
            actions.send_keys(keys[upper_item])

        else:
            # Caracter comum
            actions.send_keys(item)

    # Solta os modificadores no final
    for mod in reversed(pressed_modifiers):
        actions.key_up(mod)

    actions.perform()