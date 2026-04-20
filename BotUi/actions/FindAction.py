from BotUi.actions.abstracts.BaseAction import BaseAction
from BotUi.finders.BotTargetLocator import BotTargetLocator
from BotUi.config.BotConstants import ScrollConstants, RetryConstants



class FindAction(BaseAction):
    def __init__(self, bot_driver, bot_app, step_info):
        super().__init__(bot_driver, bot_app, step_info)
        self.scroll_attempt = 0
        self.find_retry_attempts = 0

    def run(self):
        # --- (1) Captura configurações principais ---
        object_type = self.step_info.get("object_type")

        # --- (2) Screenshot ---
        screenshot_path, screenshot_image = self.capture()

        # --- (3) Escolhe função de busca ---
        bot_target_detector = BotTargetLocator(
            image_source_path=screenshot_path, # DA ERRADO, NAO TEM AQUI O PRINT!
            debug=self.step_info.get("debug", False),
            debug_path = self.bot_app.debug_path,
            offset_x = self.step_info.get("x_coord", 0),
            offset_y = self.step_info.get("y_coord", 0),
            logger = self.get_logger()
        )

        detector_args_map = {
            "IMG": {
                "template_path": self.step_info.get("image_path"),
            },
            "TEXT": {
                "target_text": self.step_info.get("text"),
                "in_text": self.step_info.get("in_text", True),
                "position": self.step_info.get("position", 0),
                "side": self.step_info.get("side", None),

            },
        }

        # --- (4) Tenta localizar o objeto ---
        args = detector_args_map.get(object_type, {})

        target_result = bot_target_detector.dealer(
            detector_type=object_type,
            **args
        )
        if target_result.debug_image_path:
            self.bot_app.media_manager.record({
                "type": "image",
                "label": "Debug",
                "data": target_result.debug_image,
                "path": target_result.debug_image_path,
                "hash": None
            })

        # --- (5) Check se achou e aplica devida regra ---
        if target_result.error:
           executed = False
           error = target_result.log_message
        if not target_result.found:
            executed, error = self._not_find_consequence(self.step_info, target_result.log_message)
        else:
            executed, error = self._find_consequence(self.step_info, object_coord=target_result.center)
        
        return executed, error
    
    # ----------------------
    # Consequências
    # ----------------------
    def _find_consequence(self, step, object_coord):
        click_enabled = step.get("click", False)
        if_find = step.get("if_find", None)
        save_as = step.get("save_as")


        # --- (2) Save coord---
        if save_as:
            self.set_var(save_as, [float(object_coord[0]), float(object_coord[1])])

        # --- (4) Clique final ---
        if click_enabled and object_coord:
            success, log_result = self.bot_driver.click(object_coord)
            if not success:
                return False, f"[FIND] Falha ao clicar no objeto: {log_result}"

        # --- (5)  Acoes de Encontrar---
        if if_find=="retry":
            return self.run()
        
        return True, None

    def _not_find_consequence(self, step, log):
        scroll_enabled = step.get("scroll", False)
        scroll_direction = step.get("scroll_direction", ScrollConstants.DEFAULT_DIRECTION)
        until_find = step.get("until_find", None)
        optional = step.get("optional", False)

        # TODO : Remover esse chek, por hora vai ter que ser assim pq n acho uma solucao que funciione
        if scroll_enabled and until_find:
            return False, "[FIND] Não é permitido usar 'scroll' e 'until_find' ao mesmo tempo"


        # Scroll?
        if scroll_enabled and self.scroll_attempt < ScrollConstants.MAX_ATTEMPTS:
            scrolled, error = self._scroll_page(step, scroll_direction)
            if not scrolled:
                return False, f"[FIND] Erro no scroll: {error}"
            if not self._check_if_scrolled():
                self.scroll_attempt = ScrollConstants.MAX_ATTEMPTS + 1

            return self.run()
        

        # Retry Por Until Find
        if until_find=="retry" and self.find_retry_attempts <= RetryConstants.FIND_RETRY_MAX_ATTEMPTS:
            self.find_retry_attempts+=1
            return self.run() 
        
        # Find opcionais
        if optional:
            return True, "[FIND] Objeto não encontrado, mas optional=True"

        return False, f"[FIND] Objeto não encontrado: {log}"

    # ----------------------
    # Scroll Actions # TODO: Criar um manager para scroll(?)
    # ----------------------
    def _scroll_page(self, step, scroll_direction): # TODO: ESTA FIXO O VALOR, ALTERAR!
        try: 
            # --- Aplica Log ---
            self.get_logger().debug(
                f"🔄 Scrolling para localizar o objeto "
                f"({self.scroll_attempt}/{ScrollConstants.MAX_ATTEMPTS})..."
            )
            # --- Atualiza A Tentativa ---
            self.scroll_attempt += 1
            
            scroll_coord = [500, 500] # TODO: ajustar se for dinâmico

            
            # --- Aplica o Scroll ---
            self.bot_driver.scroll(
                direction=scroll_direction,
                delta_y=ScrollConstants.DISTANCE,
                coord=scroll_coord,
            )
            return True, None
        except Exception as err:
            return False, f"[FIND] Erro ao fazer scroll: {err}"

        
    def _check_if_scrolled(self):
        try:
            self.capture()
            if not self.bot_app.media_manager.has_page_changed():
                self.get_logger().warning("[FIND] Tela não mudou após scroll")
                return False
            return True
        except Exception as e:
            return False