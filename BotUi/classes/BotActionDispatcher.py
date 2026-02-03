import time

from BotUi.classes.actions.WriteAction import WriteAction
from BotUi.classes.actions.FindAction import FindAction
from BotUi.classes.actions.KeySelectionsAction import KeySelectionsAction
from BotUi.classes.actions.RunScriptAction import RunScriptAction
from BotUi.classes.actions.FindTextByColorAction import FindTextByColorAction
from BotUi.classes.actions.StopIfAction import StopIfAction
from BotUi.classes.actions.UploadAction import UploadAction
from BotUi.classes.actions.DoWhileAction import DoWhileAction



class BotActionDispatcher:
    ACTION_MAP = {
        "WRITE": WriteAction,
        "FIND": FindAction,
        "KEYS_SELECTIONS": KeySelectionsAction,
        "RUN_SCRIPT": RunScriptAction,
        "FIND_TEXT_BY_COLOR": FindTextByColorAction,
        "STOP_IF": StopIfAction,
        "UPLOAD_FILE": UploadAction,
        "DO_WHILE": DoWhileAction,
    }

    def __init__(self, bot_driver, bot_app):
        self.bot_app = bot_app
        self.bot_driver = bot_driver


    def dispatch(self, step_info) -> tuple[bool, str | None]:
        action_name = step_info.get("action")
        action_class = self.ACTION_MAP.get(action_name)

        if not action_class:
            return False, f"Ação não implementada: {action_name}"


        # Instancia a classe da ação correta
        action_instance = action_class(
            bot_driver=self.bot_driver,
            bot_app=self.bot_app,
            step_info=step_info
        )

        # Executa a ação
        task_completed, log_text =  action_instance.run()

        if log_text is not None or not task_completed:
            return False, log_text
        
        # Global Actions
        self._apply_global_step_behavior(step_info)


        return task_completed, log_text
    
    def _apply_global_step_behavior(self, step_info):
        if step_info.get("refresh"):
            self.bot_driver.reload()
        if step_info.get("wait"):
            time.sleep(step_info["wait"])
        if step_info.get("save_url"):
            self.bot_app.set_variable(
                step_info["save_url"], self.bot_driver.get_url()
            )
        # Captura final
        self.bot_app.media_manager.capture("screenshot")




