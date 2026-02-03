from BotUi.classes.abstracts.BaseAction import BaseAction
from BotUi.classes.BotTargetLocator import BotTargetLocator
from BotUi.classes.BotConstants import ScrollConstants, RetryConstants



class FindAction(BaseAction):
    def __init__(self, bot_driver, bot_app, step_info):
        super().__init__(bot_driver, bot_app, step_info)
        self.scroll_attempt = 0
        self.find_retry_attempts = 0

    def run(self):
        # --- (1) Captura configurações principais ---
        step = self.step_info
        object_type = step.get("object_type")

        # --- (2) Screenshot ---
        screenshot_path, screenshot_image = self.capture()

        # --- (3) Escolhe função de busca ---
        bot_target_detector = BotTargetLocator(
            image_source_path=screenshot_path, # DA ERRADO, NAO TEM AQUI O PRINT!
            debug=self.step_info.get("debug", False),
            debug_path = self.bot_app.debug_path,
            offset_x = step.get("x_coord", 0),
            offset_y = step.get("y_coord", 0),
            logger = self.get_logger()
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
            debug_info = {"data": debug_result, "path": debug_result_path, "label": "Debug"}
            self.bot_app.media_manager.record(debug_info)


        # --- (5) Check se achou e aplica devida regra ---
        if error is not None:
            executed = False
        elif not target_found: 
            executed, error =  self._not_find_consequence(step, error)
        else:
            executed, error =   self._find_consequence(step, object_coord=target_center) # Garantido ser <ok, error>
        
        return executed, error
    

    def _find_consequence(self, step, object_coord):
        click_enabled = step.get("click", False)
        if_find = step.get("if_find", None)
        save_as = step.get("save_as")


        # --- (2) Save coord---
        if save_as:
            self.set_var(save_as, [float(object_coord[0]), float(object_coord[1])])

        # --- (4) Clique final ---
        if click_enabled and object_coord:
            self.bot_driver.click(object_coord)

        # --- (5)  Acoes de Encontrar---
        if if_find:
            if if_find=="retry":
                return self.run()
        
        return True, None

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
            return self.run()
        

        # TODO: Fazer um check se chegou no final da pagina ou topo da pagina!
        if until_find: 
            if until_find=="retry" and self.find_retry_attempts <= RetryConstants.FIND_RETRY_MAX_ATTEMPTS:
                self.find_retry_attempts+=1
                return self.run() 
            


    
        if not optional:
            self.get_logger().debug(f"Nao foi possivel localizar o objeto.")
            return False, None
        else:
            return True, None # Nao Encontrou o objeto mas finalizou corretamente(Sem erro(devo acrescentar erro aqui(?)))!
    
    # ----------------------
    # Scroll Actions # TODO: Criar um manager para scroll(?)
    # ----------------------
    def _scroll_page(self, step, scroll_direction): # TODO: ESTA FIXO O VALOR, ALTERAR!
        try: 
            # --- Aplica Log ---
            self.get_logger().debug(
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
        self.capture() # Garante um print extra por precaucao(?) 
        if not self.bot_app.media_manager.has_page_changed():
            self.get_logger().warning("🧊 Tela não mudou após scroll, finalizando possibilidade de scroll neste step")
            return False
        return True
