from typing import Optional, Any
from dataclasses import dataclass

from BotUi.core.components import Step



@dataclass
class PipelineResult:
    success: bool
    message: Optional[str] = None

    def failed(self) -> bool:
        return not self.success

class Pipeline:
    def __init__(
            self,
            name,
            pipeline_raw, 
            bot_app, 
            bot_driver,
            debug_mode=False
        ):
        # =======================
        # External Classes
        # =======================
        self.bot_app = bot_app
        self.bot_driver = bot_driver

        # =======================
        # Pipeline Info
        # =======================
        self.name = name
        self.status = "INITIALIZED" # TODO: Transformar em uma classe de status!(PAUSED, RUNNING, ...)
        self.pipeline_raw = pipeline_raw
        self.debug_mode=debug_mode
        # =======================
        # Pipeline Info
        # =======================
        self.url = self.pipeline_raw.get("url")



    def run(self, actions_dispatch) -> PipelineResult:
        self.status = "RUNNING"

        # 1)
        status = self._pre_step()

        if not status:
            return PipelineResult(
                message=None,
                success=False
            )

        # 2)
        steps = self._get_steps()
        
        # 3) 
        message, success = self._run_steps(steps, actions_dispatch)
            


        self.status = "FINISHED"
        pipeline_result = PipelineResult(
            message=f"[Pipeline.run] {message}",
            success=success
        )

        return pipeline_result

    def _pre_step(self):
        self.bot_app.logger.info(f"[ - ] Starting Pipeline: {self.name}")
        
        # 1)
        if self.url and not self._start_url():
            return False
        
        return True
        
        
    def _start_url(self) -> bool:
        status = self.bot_driver.goto(self.url)

        if status:
            self.bot_app.logger.info(
                "[ - ] Opening URL: %s",
                self.url,
            )
        else:
            self.bot_app.logger.error(
                "[ - ] Error opening URL: %s",
                self.url,
            )

        return status
    
    def _get_steps(self):
        steps = []

        for step_info in self.pipeline_raw["steps"]:
            step = Step(bot_app=self.bot_app, bot_driver=self.bot_driver, step_raw=step_info, debug_mode=self.debug_mode)
            steps.append(step)

        return steps
    
    def _run_steps(self, steps, actions_dispatch):
        name_map = {}
        id_map = {}
        for i, step in enumerate(steps):
            step._id = f"step_{i}"

            id_map[step._id] = step

            if step.name:
                name_map[step.name] = step._id

        success = True
        message =  None
        
        current = steps[0]._id if steps else None

        while current:
            step = id_map[current]

            step_result = step.run(actions_dispatch)

            if step_result.failed():
                success = False
                message = step_result.message
                break
            
            # TRANSITION
            next_step = step_result.next
            next_step_type = step_result.next_type

            if next_step_type == "continue":
                current = self._get_next_linear(id_map, current)
                continue
            elif next_step_type == "end":
                break
            elif next_step_type == "goto":
                current = name_map.get(next_step, next_step)
                self.bot_app.logger.info(f"[Pipeline.run._run_steps] Jumping to Step: {current}")
                continue

            # fallback
            current = self._get_next_linear(id_map, current)

        return success, message
    
    def _get_next_linear(self, id_map, current_id):
        keys = list(id_map.keys())

        try:
            idx = keys.index(current_id)
            return keys[idx + 1] if idx + 1 < len(keys) else None
        except ValueError:
            return None