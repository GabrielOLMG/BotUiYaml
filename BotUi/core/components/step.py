import time
import requests


from typing import Optional, Any
from dataclasses import dataclass

from BotUi.utils.utils import resolve_variables

@dataclass
class StepResult:
    finished: bool
    success: bool
    next: str
    next_type: str
    message: Optional[str] = None




class Step:
    def __init__(
            self,
            bot_app,
            bot_driver,
            step_raw: dict,
            debug_mode: bool = False
        ):
        # =======================
        # External Classes
        # =======================
        self.bot_app = bot_app
        self.bot_driver = bot_driver

        # =======================
        # Step Info
        # =======================
        self.status = "INITIALIZED" # TODO: Transformar em uma classe de status!(PAUSED, RUNNING, ...)
        self.step_raw = step_raw
        self.debug_mode = debug_mode
        # =======================
        # Step Info
        # =======================
        self.name=self.step_raw.get("name")
        self.description = self.step_raw.get("helper")

        self._id = None





    def run(self, actions_dispatch) -> StepResult:
        self.status = "RUNNING"

        # 0) 
        self.resolved_step = self._resolve_step_vars()

        # 1)
        self._pre_action()

        # 2) 
        actions_dispatch_result = actions_dispatch.dispatch(self.resolved_step)
        
        # 3)
        post_action_result = self._post_action(actions_dispatch_result)

        # 4)
        if post_action_result["type"] == "debug":
            return self._debug_mode(actions_dispatch)


        self.status = "FINISHED"
        step_result = StepResult(
            finished=actions_dispatch_result.finished,
            success=actions_dispatch_result.success,
            message=f"[Step.run] {actions_dispatch_result.message}",
            next=post_action_result["target"],
            next_type=post_action_result["type"]

        )

        return step_result
    
    def _pre_action(self):
        if self.name:
            self.bot_app.logger.info(f"[ -- ] Initializing step with name: {self.name} - internal ID: {self._id}")
        else:
            self.bot_app.logger.info(f"[ -- ] Initializing a step without a name, but with an internal ID: {self._id}")

            
        if self.description:
            self.bot_app.logger.info("[ -- ] Step: %s", self.description)

    def _post_action(self, actions_dispatch_result):
        next_config = self.resolved_step.get("next")
        text = f"[Step.run._post_action] {actions_dispatch_result.message} | Step Info: {self.resolved_step}"

        if not (actions_dispatch_result.finished or next_config or self.debug_mode):
            self.bot_app.logger.error(text)
        elif not actions_dispatch_result.success:
            self.bot_app.logger.warning(text)

        # 1)

        if not actions_dispatch_result.success:
            if next_config and False in next_config:
                return {
                    "type": "goto",
                    "target": next_config[False]
                }
            
            if self.debug_mode and not actions_dispatch_result.success:
                return {
                    "type": "debug",
                    "target": None
                }
            
            return {
                "type": "end",
                "target": None
            }

        if next_config and True in next_config:
            return {
                "type": "goto",
                "target": next_config[True]
            }

        return {
            "type": "continue",
            "target": None
        }



    def _resolve_step_vars(self):
        resolved = {}

        for key, value in self.step_raw.items():
            resolved[key] = resolve_variables(value, self.bot_app.data_store, ignore_miss=False)

        return resolved
    
    def _debug_mode(self, actions_dispatch):
        self.status = "PAUSED"
        while True:
            self.bot_app.logger.info("Step pausado...para modificar eloe, basta ir no endpoint de update. e atualizar os devidos parametros")

            response = requests.get(f"http://botui_api:8000/step-update/{self.name}")
            data = response.json()
            if data:
                self.step_raw.update(data["parameters"])
                self.debug_mode =data.get("debug", True)

                self.bot_app.logger.info(f"Step atualizado via API: {data}")

                break

            time.sleep(2)
        
        return self.run(actions_dispatch)