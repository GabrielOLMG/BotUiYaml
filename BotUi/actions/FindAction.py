from BotUi.actions.abstracts.BaseAction import BaseAction
from BotUi.finders.BotTargetLocator import BotTargetLocator
from BotUi.config.BotConstants import ScrollConstants



class FindAction(BaseAction):
    def __init__(self, bot_driver, bot_app, step_info):
        super().__init__(bot_driver, bot_app, step_info)
        self.scroll_attempt = 0
        self.find_retry_attempts = 0

    def run(self):
        # 1)
        object_type = self.step_info.get("object_type")

        # 2) 
        target_result = self._execute_find(object_type)
        if target_result.error:
            return False, f"[FindAction.run] {target_result.log_message}"

        # 3)    
        executed, error = self._evaluate(target_result)
        
        return executed, error
    

    def _execute_find(self, object_type):
        # 1)
        screenshot_path, _ = self.capture()

        # 2)
        bot_target_detector = BotTargetLocator(
            image_source_path=screenshot_path,
            debug=self.step_info.get("debug", False),
            debug_path = self.bot_app.debug_path,
            offset_x = self.step_info.get("x_coord", 0),
            offset_y = self.step_info.get("y_coord", 0),
            logger = self.get_logger()
        )

        # 3) 
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
        args = detector_args_map.get(object_type, {})

        # 4)
        target_result = bot_target_detector.dealer(
            detector_type=object_type,
            **args
        )

        # 5) 
        if target_result.debug_image_path:
            self.bot_app.media_manager.record({
                "type": "image",
                "label": "Debug",
                "data": target_result.debug_image,
                "path": target_result.debug_image_path,
                "hash": None
            })
        return target_result
    
    

    # ----------------------
    # Consequências
    # ----------------------
    def _evaluate(self, target_result):
        # TODO: Aqui vou poder fazer os operadores , se count eq/gt... ou exit

        if target_result.found: # step_info.get('operator').get('type') == exist $ PADRAO!
            executed, error = self._if_find(self.step_info, object_coord=target_result.center)
        elif not target_result.found: # step_info.get('operator').get('type') == not_exist
            executed, error = self.if_not_find(self.step_info)

        return executed, error

    def _if_find(self, step, object_coord):
        # 1)
        save_as = step.get("save_as")
        if save_as:
            self.set_var(save_as, [float(object_coord[0]), float(object_coord[1])])

        # 2)
        click_enabled = step.get("click", False)
        if click_enabled and object_coord:
            success, log_result = self.bot_driver.click(object_coord)
            if not success:
                return False, f"[FIND] Falha ao clicar no objeto: {log_result}"
        
        return True, None

    def if_not_find(self, step):
        scroll_enabled = step.get("scroll", False)
        scroll_direction = step.get("scroll_direction", ScrollConstants.DEFAULT_DIRECTION)

        # Scroll?
        if scroll_enabled and self.scroll_attempt < ScrollConstants.MAX_ATTEMPTS:
            scrolled, error = self._scroll_page(step, scroll_direction)
            if not scrolled:
                return False, f"[FIND] Erro no scroll: {error}"
            if not self._check_if_scrolled():
                self.scroll_attempt = ScrollConstants.MAX_ATTEMPTS + 1

            return self.run()
                
        return False, "[FIND] Objeto não encontrado"

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