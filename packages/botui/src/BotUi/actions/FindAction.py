from BotUi.actions.abstracts import BaseAction, BaseActionResult
from BotUi.finders.BotTargetLocator import BotTargetLocator
from BotUi.config.BotConstants import ScrollConstants, FindConstants



class FindAction(BaseAction):
    def __init__(self, bot_driver, bot_app, step_info):
        super().__init__(bot_driver, bot_app, step_info)
        self.attempts_to_find = 0

    def run(self):
        # 1)
        object_type = self.step_info.get("object_type")

        interaction = self.step_info.get("interaction", {})

        search_strategy = self.step_info.get("search_strategy", {})
        scroll_enabled = search_strategy.get("scroll", False)


        # 2)
        attempts = 0
        max_attempts = FindConstants.MAX_ATTEMPTS if scroll_enabled else 1

        while attempts < max_attempts:
            target_result = self._find_target(object_type, offset=interaction.get("offset", {}))
            if target_result.error:
                return BaseActionResult(
                        finished=False,
                        success=False,
                        message=f"[FindAction.run] {target_result.log_message}"
                    )

            success = self._evaluate_target_result(target_result)

            # -------- FOUND -----------
            if success:
                error = self._apply_on_found(target_result, interaction)
                if error:
                    return BaseActionResult(
                            finished=False,
                            success=False,
                            message=f"[FindAction.run] {error}"
                        )
                return BaseActionResult(
                            finished=True,
                            success=True,
                            message=None
                        )
            
            # -------- NOT FOUND --------
            if not scroll_enabled:
                break
            
            scrolled, error = self._scroll_page(self.step_info, search_strategy)
            if not scrolled:
                return BaseActionResult(
                    finished=False,
                    success=False,
                    message=f"[FindAction.run] {error}"
                )

            if not self._check_if_scrolled():
                break

            self.attempts_to_find += 1

        return BaseActionResult(
            finished=True,
            success=False,
            message="[FindAction.run] Object not found"
        )
    
    def _find_target(self, object_type, offset):
        # 1)
        screenshot_path, _ = self.capture()

        # 2)
        bot_target_detector = BotTargetLocator(
            image_source_path=screenshot_path,
            debug=self.step_info.get("debug", False),
            debug_folder = self.bot_app.debug_folder,
            offset = offset,
            logger = self.get_logger()
        )

        # 3) 
        detector_args_map = {
            "IMG": {
                "template_path": self.step_info.get("image_path"),
                "search_area": self.step_info.get("search_area", {})
            },
            "TEXT": {
                "target_text": self.step_info.get("text"),
                "in_text": self.step_info.get("in_text", True),
                "position": self.step_info.get("position", 0),
                "search_area": self.step_info.get("search_area", {})
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
    
    def _evaluate_target_result(self, target_result):
        # {"type": "count", "op": "gt","value": 2}
        # {"type": "exists", "value": True} # Default!!
        operator = self.step_info.get("operator", {"type": "exists", "value": True}) # Ainda nao existe, mas preparando para quando existir!
        op_type = operator.get("type")

        if op_type == "exists":
            return target_result.found == operator.get("value", True)
        elif op_type == "count":
            count = len(target_result.matches)
            op = operator.get("op", "eq")
            value = operator.get("value", 1)

            if op == "gt":
                return count > value
            if op == "eq":
                return count == value
        else:
            raise ValueError("Operator Type does not exist.")
        
    def _apply_on_found(self, target_result, interaction):
        object_coord = target_result.center
        save_as = self.step_info.get("save_as")


        # 1. save
        if save_as and object_coord:
            self.set_var(save_as, [float(object_coord[0]), float(object_coord[1])])

        # 2. Early return
        if not interaction or not interaction.get("type"):
            return None
        
        interaction_type = interaction["type"]

        # 3. Interaction Type Check
        if interaction_type == "CLICK":
            success, error = self.bot_driver.click(object_coord)
            if not success:
                return f"[FindAction._apply_on_found.click]{error}"
        elif interaction_type == "UPLOAD":
            file_path = interaction.get("file_path", None)
            if not file_path:
                return f"[FindAction._apply_on_found.upload] To upload a file, you need to have the 'file_path' field in 'interaction'." 
            success, error = self.bot_driver.upload_file(file_path, object_coord)
            if not success:
                return f"[FindAction._apply_on_found.upload] {error}"

        return None
    
    def _scroll_page(self, step_info, search_strategy):
        scroll_direction = search_strategy.get("direction", ScrollConstants.DEFAULT_DIRECTION)

        # --- Aplica Log ---
        self.get_logger().debug(
            f"[FindAction._scroll_page] Using scroll(Direction: {scroll_direction}) to locate the object "
            f"({self.attempts_to_find}/{ScrollConstants.MAX_ATTEMPTS})..."
        )

        scroll_coord = [500, 500] # TODO: ajustar se for dinâmico

        # --- Aplica o Scroll ---
        success, error = self.bot_driver.scroll(
            direction=scroll_direction,
            delta_y=ScrollConstants.DISTANCE,
            coord=scroll_coord,
        )
        if not success:
                return f"[FindAction._scroll_page] Failed to execute the drive scroll action: {error}"

        return True, None

    def _check_if_scrolled(self):
        try:
            self.capture()
            if not self.bot_app.media_manager.has_page_changed():
                self.get_logger().warning("[FindAction._check_if_scrolled] The screen did not change when scrolling was applied; scrolling action ended.")
                return False
            return True
        except Exception as e:
            return False


