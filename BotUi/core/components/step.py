import time
import requests


from typing import Optional, Any
from dataclasses import dataclass

from BotUi.utils.utils import resolve_variables

@dataclass
class StepResult:
    success: bool
    message: Optional[str] = None

    def failed(self) -> bool:
        return not self.success



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




    def run(self, actions_dispatch) -> StepResult:
        self.status = "RUNNING"

        # 0) 
        self.resolved_step = self._resolve_step_vars()

        # 1)
        self._pre_action()

        # 2) 
        actions_dispatch_result = actions_dispatch.dispatch(self.resolved_step)
        
        # 3)
        self._post_action(actions_dispatch_result, actions_dispatch)
        
        self.status = "FINISHED"
        step_result = StepResult(
            message=f"[Step.run] {actions_dispatch_result.message}",
            success=actions_dispatch_result.success
        )

        return step_result
    
    def _pre_action(self):
        self.bot_app.logger.info(f"[ -- ] Starting Step: {self.name if self.name else 'Unnamed'}")
            
        if self.description:
            self.bot_app.logger.info("[ -- ] Step: %s", self.description)

    def _post_action(self, actions_dispatch_result, actions_dispatch):
        # 0) 
        if self.debug_mode and actions_dispatch_result.failed():
            return self._debug_mode(actions_dispatch)


        if actions_dispatch_result.failed(): 
            self.bot_app.logger.error("[Step.run._post_action] %s | Step Info: %s", actions_dispatch_result.message, self.resolved_step)

    def _resolve_step_vars(self):
        resolved = {}

        for key, value in self.step_raw.items():
            resolved[key] = resolve_variables(value, self.bot_app.data_store, ignore_miss=False)

        return resolved
    
    def _debug_mode(self, actions_dispatch):
        self.status = "PAUSED"
        while True:
            self.bot_app.logger.info("Step pausado...para modificar eloe, basta ir no endpoint de update. e atualizar os devidos parametros")

            response = requests.get(f"http://host.docker.internal:8000/step-update/{self.name}")
            data = response.json()
            if data:
                self.step_raw.update(data["parameters"])
                self.debug_mode =data.get("debug", True)

                self.bot_app.logger.info(f"Step atualizado via API: {data}")

                break

            time.sleep(1)
        
        self.run(actions_dispatch)