import os
import subprocess

from ..functions.selenium_functions import *
from ..functions.key_map import *
from ..functions.utils import *
from ..functions.image_functions import *




class BotActions:
    """
    Classe para centralizar todas as ações possíveis em uma pipeline BotUI.
    Mantém driver, data_store e funções comuns.
    """

    def __init__(self, driver, step_info, logger, screenshots_path, data_store=None):
        self.driver = driver
        self.data_store = data_store if data_store is not None else {}


        self.step_info = step_info
        self.logger = logger

        # Scroll Confg
        self.scroll_attempt = 0
        self.scroll_max_attempts = 50
        self.scroll_distance = 500
        self.scroll_direction_default = "DOWN"
        

        # Screenshots
        self.screenshots_path = screenshots_path
        self.screenshot_check_page = None

        self.init_variables()


        self.ACTION_MAP = {
                "WRITE": self.write,
                "FIND": self.find,
                "KEYS_SELECTIONS": self.keys_selections,
                "RUN_SCRIPT": self.run_script,
                "FIND_TEXT_BY_COLOR": self.find_text_by_color,
                "STOP_IF": self.stop_if,
                "UPLOAD_FILE": self.upload_file
            }

    def run_action(self):
        action = self.step_info["action"]
        function = self.ACTION_MAP.get(action)

        if not function:
            False, f"Ação não implementada: {action}"
        
        self._take_screenshot()
        try:
            result = function()
            if not isinstance(result, bool) and not result[0]:
                return False, result[1] 
            
            if self.step_info.get("refresh", False):
                self.driver.refresh()

            wait_time = self.step_info.get("wait")
            if wait_time:
                self.logger.debug("⏱ Aguardando %.2f segundos", wait_time)
                time.sleep(wait_time)
            
            if self.step_info.get("save_url", None):
                self.data_store[self.step_info.get("save_url")] = self.driver.current_url
            
        except Exception as e:
            return False, f"Erro ao executar step '{self.step_info}': {e}" 
        
        self._take_screenshot()

        return True, None

    def debug(self, coord, image_path):
        screenshot_parent = os.path.dirname(self.screenshot_check_page)
        output_path = os.path.join(screenshot_parent, "debug.png") 
        return marcar_x_na_imagem(image_path, coord, output_path)

    def init_variables(self):
        for key_name  in self.step_info:
            self.step_info[key_name] = resolve_variables(self.step_info[key_name], self.data_store)

    def _take_screenshot(self, screenshot_name="screenshot_check_page.png"):
        full_screenshot_path = os.path.join(self.screenshots_path, screenshot_name)
        self.screenshot_check_page = get_screenshot(self.driver, full_screenshot_path) 

        return self.screenshot_check_page

    # ----------------------
    # Actions
    # ----------------------~

    def find(self):
        """
        Localiza um objeto na tela (imagem ou texto), com suporte a scroll e clique.
        Retorna True em sucesso, ou (False, mensagem) em falha.
        """

        # --- 1️⃣ Captura configurações principais ---
        step = self.step_info
        object_type = step.get("object_type")
        scroll_enabled = step.get("scroll", False)
        scroll_direction = step.get("scroll_direction", self.scroll_direction_default)
        offset_x = step.get("x_coord", 0)
        offset_y = step.get("y_coord", 0)
        debug_mode = step.get("debug", False)
        optional = step.get("optional", False)
        click_enabled = step.get("click", False)

        # --- 2️⃣ Escolhe função de busca ---
        find_fn_map = {
            "IMG": lambda: find_image_center(
                screenshot_path=self.screenshot_check_page,
                template_path=step["image_path"]
            ),
            "TEXT": lambda: encontrar_texto_central(
                image_path=self.screenshot_check_page,
                text=step["text"],
                contain_=self.step_info.get("in_text", True),
                debug=self.step_info.get("debug", False)
            ),
        }

        if object_type not in find_fn_map:
            return False, f"[FIND] Tipo de objeto inválido: {object_type}"

        # --- 3️⃣ Tenta localizar o objeto ---
        status, error_text, coord = find_fn_map[object_type]()

        # --- 4️⃣ Caso falhe, tenta scrollar e repetir ---
        if not status:
            if scroll_enabled and self.scroll_attempt < self.scroll_max_attempts:
                self.logger.debug(
                    f"🔄 Scrolling to locate the object "
                    f"({self.scroll_attempt}/{self.scroll_max_attempts})..."
                )
                self.scroll_attempt += 1

                scroll_status, scroll_error, scroll_coord = find_image_center(
                    screenshot_path=self.screenshot_check_page,
                    template_path=step["scroll_image_path"]
                )

                if not scroll_status:
                    return False, f"[FIND] Falha ao localizar imagem de scroll: {scroll_error}"
                drag_vertical(
                    driver=self.driver,
                    coord=scroll_coord,
                    direction=scroll_direction,
                    delta_y=self.scroll_distance
                )
                self._take_screenshot()
                return self.find()  # chamada recursiva
            else:
                if not optional:
                    return False, f"[FIND] {error_text}"
                else:
                    return True

        # --- 5️⃣ Aplica offset (x, y) ---
        if offset_x or offset_y:
            coord = (coord[0] + offset_x, coord[1] + offset_y)

        # --- 6️⃣ Modo debug ---
        if debug_mode:
            self.debug(coord, self.screenshot_check_page)

        # --- 7️⃣ Clique final ---
        if click_enabled and coord:
            click_coord(self.driver, coord)

        # --- 8️⃣ Retorno final ---
        return True

    def write(self):
        if "text" in self.step_info:
            text = self.step_info["text"]
            write_input(self.driver, text)
            return True
        elif "file_path" in self.step_info:
            path = self.step_info["file_path"]
            text = open_file(path)
            write_input(self.driver, text)
            return True
        else:
            return False, "Flag Para Write Não Existe!"

    def keys_selections(self):
        send_key_sequence(self.driver, self.step_info["keys"])
        return True

    def run_script(self):
        # TODO: Init Melhorar
        script_path = self.step_info.get("script_path")
        script_path = resolve_variables(script_path, self.data_store)
        script_flags = self.step_info.get("flags", None)
        script_flags = resolve_variables(script_flags, self.data_store)
        # TODO: Fim Melhorar

        save_as = self.step_info.get("save_as")

        if not script_path:
            return False, "RUN_SCRIPT requires 'script_path'"
        if not os.path.exists(script_path):
            return False, f"RUN_SCRIPT file {script_path} does not exist"

        try:
            # Monta a lista de argumentos
            cmd = ["bash", script_path]
            if script_flags:
                # Divide em múltiplos argumentos se houver espaços
                if isinstance(script_flags, str):
                    cmd.extend(script_flags.split())
                elif isinstance(script_flags, list):
                    cmd.extend(script_flags)

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            output = result.stdout.strip()

        except subprocess.CalledProcessError as e:
            return False, f"Script {script_path} failed:\n{e.stderr}"

        if save_as:
            self.data_store[save_as] = output
        return True

    def find_text_by_color(self):
        color = self.step_info.get("color")
        save_as = self.step_info.get("save_as")

        text_detected = extract_text_from_image(self.screenshot_check_page, color)

        if save_as:
            self.data_store[save_as] = text_detected
        return True

    def stop_if(self):
        result = evaluate_condition(self.step_info["condition"])
        if result:
            return False, f"Condition To Stop True: {self.step_info['condition']}=={result}"
        return True

    def upload_file(self):
        print("#NOT WORKING!!!!!!!")
        upload_file(self.driver, self.step_info["file_path"])

        return True
    # ----------------------
    # Helper genéricos
    # ----------------------
    def update_data_store(self, key, value):
        self.data_store[key] = value

    def get_data_store(self, key, default=None):
        return self.data_store.get(key, default)