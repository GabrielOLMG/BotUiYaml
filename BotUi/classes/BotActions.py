import os
import time

from ..functions.utils import *
from ..functions.image_functions import *
from .BotConstants import *
from .BotTargetLocator import BotTargetLocator


class BotActions:
    """
    Classe para centralizar todas as ações possíveis em uma pipeline BotUI.
    Mantém driver, data_store e funções comuns.
    """

    def __init__(self, bot_driver, bot_app, step_info):
        self.bot_driver = bot_driver
        self.bot_app = bot_app
        self.step_info = step_info

        # Counts
        self.scroll_attempt = 0
        self.find_retry_attempts = 0

        # Screenshots
        self.screenshot_check_page = None
        self.screenshots_action_history = []
        

        self.ACTION_MAP = {
                "WRITE": self.write,
                "FIND": self.find,
                "KEYS_SELECTIONS": self.keys_selections,
                "RUN_SCRIPT": self.run_script,
                "FIND_TEXT_BY_COLOR": self.find_text_by_color,
                "STOP_IF": self.stop_if,
                "UPLOAD_FILE": self.upload_file,
                "DO_WHILE": self.do_while
            }

    def run_action(self):
        action = self.step_info["action"]
        function = self.ACTION_MAP.get(action)
        wait_time = self.step_info.get("wait")
        refresh = self.step_info.get("refresh", False)
        save_url = self.step_info.get("save_url", None)

        if not function:
            log_text = f"Ação não implementada: {action}"
            return False, log_text
        
        # [1]
        self._take_screenshot()

        # [2]
        task_completed, error = function() # Cada action DEVE retornar: (bool task_completed, Optional[str] error)
        if error is not None:
            log_text = f"❌ Acao '{action}' foi finalizada com erro: {error}"
            return False, log_text
        elif not task_completed:
            log_text = f"❓ Acao '{action}' nao finalizou sua task como deveria(Reveja os parametros passados)." #TODO: Como posso saber o motivo?
            return False, log_text
        
        # [3]
        if refresh:
            self.bot_app.logger.debug("Dando refresh na pagina")
            self.bot_driver.reload()
        if wait_time:
            self.bot_app.logger.debug("Aguardando %.2f segundos", wait_time)
            time.sleep(wait_time)
        if save_url:
            self.bot_app.logger.debug(f"Salvando URL {self.bot_driver.get_url()} na variavel {save_url}")
            self.data_store[save_url] = self.bot_driver.get_url()
            
        self._take_screenshot()

        return True, None

    def _take_screenshot(self):
        self.screenshot_check_page, data = self.bot_driver.get_screenshot(self.bot_app.screenshot_path) 
        self.screenshots_action_history.append(data)
        return self.screenshot_check_page, data

    # ----------------------
    # Main Actions
    # ----------------------
    # TODO: Garantir Que Esta 100%!
    def do_while(self):
        do_actions = self.step_info["do"]
        while_condition_actions = self.step_info["while_condition"]
        allowed_while_actions = ["FIND"]
        keep_going = True

        while keep_going:
            for i, do_action in enumerate(do_actions): # As Acoes Nao podem dar Erro
                print(f"fazendo action_{i}")
                actions = BotActions(
                    bot_driver=self.bot_driver,
                    bot_app=self.bot_app,
                    step_info=do_action,
                )
                print(f"iniciando acao do Action_{i}")

                action_bool, action_error_log = actions.run_action()
                if not action_bool: 
                    return action_bool, action_error_log

            for while_action in while_condition_actions: # O while por hora pode dar erro, so se 
                if while_action["action"] not in allowed_while_actions:
                    return False, f"Atualmente o while pode apenas conter as acoes: {allowed_while_actions}"
                actions = BotActions(
                    bot_driver=self.bot_driver,
                    bot_app=self.bot_app,
                    step_info=while_action,
                )
                while_bool, while_error_log = actions.run_action()
                if while_error_log: 
                    return while_bool, while_error_log 
                
                if not while_bool: # TODO: Melhorar logica, pq por hora so funciina com FIND!
                    keep_going = False
                    break
                # TODO: Como que vou finalizar o while? nao posso permitir que finalize com erros
                # if not while_bool: 
                #     keep_going= False
                #     break
        return True

    def find(self):
        """
        Localiza um objeto na tela (imagem ou texto), com suporte a scroll e clique.
        Retorna True em sucesso, ou (False, mensagem) em falha.
        """

        # --- (1) Captura configurações principais ---
        step = self.step_info
        object_type = step.get("object_type")

        # --- (2) Screenshot ---
        self._take_screenshot()

        # --- (3) Escolhe função de busca ---
        bot_target_detector = BotTargetLocator(
            image_source_path=self.screenshot_check_page,
            debug=self.step_info.get("debug", False),
            debug_path = self.bot_app.debug_path,
            offset_x = step.get("x_coord", 0),
            offset_y = step.get("y_coord", 0),
            logger = self.bot_app.logger
        )

        detector_args_map = {
            "IMG": {
                "template_path": step.get("image_path"),
            },
            "TEXT": {
                "target_text": step.get("text"),
                "contain": self.step_info.get("in_text", True),
            },
        }

        # --- (4) Tenta localizar o objeto ---
        args = detector_args_map.get(object_type, {})
        target_found, error, target_center, (debug_result_path, debug_result) = bot_target_detector.dealer(
            detector_type=object_type,
            **args
        )

        if debug_result_path:
            self.screenshots_action_history.append(debug_result)


        # --- (5) Check se achou e aplica devida regra ---
        if error is not None:
            return False, error
        elif not target_found: 
            return self._not_find_consequence(step, error)
        else:
            return self._find_consequence(step, object_coord=target_center)

    def write(self):
        allowed_fields = {"text", "file_path"}
        present_fields = allowed_fields & self.step_info.keys()

        if not present_fields:
            return False, "WRITE requer 'text' ou 'file_path'"

        if len(present_fields) > 1:
            return False, f"WRITE não pode ter {' e '.join(list(allowed_fields))} ao mesmo tempo"

        field = present_fields.pop()
        value = self.step_info[field]
        if field == "file_path":
            value = open_file(value)
            
        executed, error = self.bot_driver.write(value)
        return executed, error

    def keys_selections(self):
        executed, error = self.bot_driver.key_sequence(self.step_info["keys"]) 
        return executed, error

    def run_script(self):
        script_path, flags = self._resolve_script_inputs()
        
        if not self._check_path(script_path):
            return False, f"RUN_SCRIPT file {script_path} does not exist"

        executed, error, output = run_script(script_path, flags)

        self._save_output(output, error)

        return executed, error

    def find_text_by_color(self):
        color = self.step_info.get("color")

        executed, error, output = extract_text_from_image(self.screenshot_check_page, color)

        self._save_output(output, error)
        return executed, error

    def stop_if(self):
        executed, error, output = evaluate_condition(self.step_info["condition"])
        if not error and output:
            return False, f"Condition To Stop True: {self.step_info['condition']}=={output}"
        
        return executed, error

    def upload_file(self):
        raw_coord = self.step_info.get("coord")
        file_path = self.step_info["file_path"]

        coord = self._parse_coord(raw_coord)
        if coord is None:
            return False, "UPLOAD error reading upload coordination"

        if not self._check_path(file_path):
            return False, f"UPLOAD file {file_path} does not exist"

        executed, error = self.bot_driver.upload_file(file_path, coord)
        self._take_screenshot()
        return executed, error

    # ----------------------
    # RunScript Actions Secondary Functions
    # ----------------------
    def _resolve_script_inputs(self):
        path = resolve_variables(
            self.step_info.get("script_path"),
            self.data_store
        )

        flags = resolve_variables(
            self.step_info.get("flags"),
            self.data_store
        )

        return path, flags

    # ----------------------
    # Find Actions Secondary Functions
    # ----------------------
    def _scroll_page(self, step, scroll_direction): # TODO: ESTA FIXO O VALOR, ALTERAR!
        try: 
            # --- Aplica Log ---
            self.bot_app.logger.debug(
                f"🔄 Scrolling to locate the object "
                f"({self.scroll_attempt}/{ScrollConstants.MAX_ATTEMPTS})..."
            )
            # --- Atualiza A Tentativa ---
            self.scroll_attempt += 1
            
            # TODO: REMOVER E GARANTIR QUE FUNCIONA!
            """
            # --- Localiza Scroll Na Pagina ---
            scroll_status, scroll_error, scroll_coord = find_image_center(
                screenshot_path=self.screenshot_check_page,
                template_path=step["scroll_image_path"]
            )
            if not scroll_status:
                return False, f"[FIND] Falha ao localizar imagem de scroll: {scroll_error}"
            """
            scroll_coord = [500, 500]

            
            # --- Aplica o Scroll ---
            self.bot_driver.scroll(
                direction=scroll_direction,
                delta_y=ScrollConstants.DISTANCE,
                coord=scroll_coord,
            )
            return True, None
        except Exception as err:
            return False, err
    
    def _check_if_scrolled(self):
        # TEm como objetivo saber se chegou no fim da pagina ou n, mas podes er usado para outras coisas em momentos futuros
        # TODO: armazenar hashes para agilizar este processo, ao menos a primeira parte: Parte meio lenta!
        hash_before_scroll = hash_from_bytes(self.screenshots_action_history[-1])
        self._take_screenshot()
        hash_after_scroll = hash_from_bytes(self.screenshots_action_history[-1])

        if hash_before_scroll == hash_after_scroll:
            self.bot_app.logger.warning("🧊 Tela não mudou após scroll, finalizando possibilidade de scroll neste step")
            return False
        return True

    def _not_find_consequence(self, step, error_text):
        scroll_enabled = step.get("scroll", False)
        scroll_direction = step.get("scroll_direction", ScrollConstants.DEFAULT_DIRECTION)
        until_find = step.get("until_find", None)
        optional = step.get("optional", False)

        # TODO : Remover esse chek, por hora vai ter que ser assim pq n acho uma solucao que funciione
        if scroll_enabled and until_find:
            return False, "[FIND] não é permitido usar 'scroll' e 'until_find' ao mesmo tempo"

        # Continua dando scroll?
        if scroll_enabled and self.scroll_attempt < ScrollConstants.MAX_ATTEMPTS:
            scrolled, error = self._scroll_page(step, scroll_direction)
            if not scrolled:
                return False, error
            scrolled = self._check_if_scrolled()
            if not scrolled:
                self.scroll_attempt = ScrollConstants.MAX_ATTEMPTS + 1 # Se nao teve diferenca visual entre o antes do scroll e o depois, entao nao tem pq continuar dando scroll
            return self.find()
        

        # TODO: Fazer um check se chegou no final da pagina ou topo da pagina!
        if until_find: 
            if until_find=="retry" and self.find_retry_attempts <= RetryConstants.FIND_RETRY_MAX_ATTEMPTS:
                self.find_retry_attempts+=1
                return self.find() 
            


    
        if not optional:
            self.bot_app.logger.debug(f"Nao foi possivel localizar o objeto.")
            return False, None
        else:
            return True, None # Nao Encontrou o objeto mas finalizou corretamente!
    
    def _find_consequence(self, step, object_coord):
        click_enabled = step.get("click", False)
        if_find = step.get("if_find", None)

        # --- (2) Save coord---
        self._save_output([float(object_coord[0]), float(object_coord[1])], error=False)

        # --- (4) Clique final ---
        if click_enabled and object_coord:
            self.bot_driver.click(object_coord)

        # --- (5)  Acoes de Encontrar---
        if if_find:
            if if_find=="retry":
                return self.find()
        
        return True, None

    # ----------------------
    # Helper genéricos
    # ----------------------
    def update_data_store(self, key, value):
        self.data_store[key] = value

    def get_data_store(self, key, default=None):
        return self.data_store.get(key, default)
    
    def _save_output(self, output, error):
        save_as = self.step_info.get("save_as")
        if save_as and not error:
            self.data_store[save_as] = output

    def _check_path(self, path: str) -> bool:
        return os.path.exists(path)

    def _parse_coord(self, coord):
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
