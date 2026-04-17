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
        self._post_action(actions_dispatch_result)
        

        action_completed, action_log = actions_dispatch_result # TODO: No futuro isso vai ser uma classe, entao irei ter mais controle!


        self.status = "FINISHED"
        step_result = StepResult(
            message=f"[Step.run] {action_log}",
            success=action_completed
        )

        # TODO: Ideia para o futuro: Ativar modo debug, se endpoint debug for ativado -> Permite pausar esse step e voltar a correr ele(e no futuro alterar tb)!

        return step_result
    
    def _pre_action(self):
        self.bot_app.logger.info(f"[ -- ] Starting Step: {self.name if self.name else 'Unnamed'}")
            
        if self.description:
            self.bot_app.logger.info("[ -- ] Step: %s", self.description)

    def _post_action(self, actions_dispatch_result):
        action_completed, action_log = actions_dispatch_result # TODO: No futuro isso vai ser uma classe, entao irei ter mais controle!
        
        if action_log: 
            self.bot_app.logger.error("[ -- ] %s | Step Info: %s", action_log, self.resolved_step)



    def _resolve_step_vars(self):
        resolved = {}

        for key, value in self.step_raw.items():
            resolved[key] = resolve_variables(value, self.bot_app.data_store, ignore_miss=False)

        return resolved