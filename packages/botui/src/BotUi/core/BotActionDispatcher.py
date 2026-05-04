import time
import requests

from typing import Optional, Any
from dataclasses import dataclass

from BotUi.actions.WriteAction import WriteAction
from BotUi.actions.FindAction import FindAction
from BotUi.actions.KeySelectionsAction import KeySelectionsAction
from BotUi.actions.RunScriptAction import RunScriptAction
from BotUi.actions.FindTextByColorAction import FindTextByColorAction
from BotUi.actions.StopIfAction import StopIfAction
from BotUi.actions.ImportActionsAction import ImportActionsAction

@dataclass
class BotActionDispatcherResult:
    finished: bool
    success: bool
    message: Optional[str] = None

class BotActionDispatcher:
    ACTION_MAP = {
        "WRITE": WriteAction,
        "FIND": FindAction,
        "KEYS_SELECTIONS": KeySelectionsAction,
        "RUN_SCRIPT": RunScriptAction,
        "FIND_TEXT_BY_COLOR": FindTextByColorAction,
        "STOP_IF": StopIfAction,
        "IMPORT_ACTIONS": ImportActionsAction,
    }

    def __init__(self, bot_driver, bot_app):
        self.bot_app = bot_app
        self.bot_driver = bot_driver


    def dispatch(self, step_info) -> tuple[bool, str | None]:
        action_name = step_info.get("action")
        action_class = self.ACTION_MAP.get(action_name)

        if not action_class:
            return BotActionDispatcherResult(
                finished=False,
                success=False,
                message="[BotActionDispatcher.dispatch] Action not implemented"
            )


        # Instancia a classe da ação correta
        action_instance = action_class(
            bot_driver=self.bot_driver,
            bot_app=self.bot_app,
            step_info=step_info
        )

        # Executa a ação
        action_result =  action_instance.run()

        if not action_result.finished:
            return BotActionDispatcherResult(
                finished=False,
                success=False,
                message=f"[BotActionDispatcher.dispatch] {action_result.message}"
            )
        
        # Global Actions
        self._apply_global_step_behavior(step_info)

        return BotActionDispatcherResult(
                finished=True,
                success=action_result.success,
                message=f"[BotActionDispatcher.dispatch] {action_result.message}" if action_result.message else None
            )
    
    
    def _apply_global_step_behavior(self, step_info): #TODO: Aqui ou no post action do step?
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




