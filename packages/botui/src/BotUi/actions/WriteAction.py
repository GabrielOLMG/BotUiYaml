from BotUi.utils.utils import open_file
from BotUi.actions.abstracts import BaseAction, BaseActionResult




class WriteAction(BaseAction):
    def __init__(self, bot_driver, bot_app, step_info):
        super().__init__(bot_driver, bot_app, step_info)

        self.allowed_fields = ["text", "file_path"]

    def run(self) -> BaseActionResult:
        validated, log_text, field = self._validate()

        if not validated:
            return BaseActionResult(
                finished=False,
                success=False,
                message=log_text
            )

        value = self.step_info[field]
        if field == "file_path":
            value = open_file(value)
            
        success, log_text = self.bot_driver.write(value)

        return BaseActionResult(
                finished=True,
                success=success,
                message=f"[WriteAction.run] {log_text}" if log_text else None
            )

    def _validate(self):
        present_fields = set(self.allowed_fields) & self.step_info.keys()

        if not present_fields:
            return False, f"[WriteAction._validate] Acao Requer {' ou '.join(self.allowed_fields)}", None

        if len(present_fields) > 1:
            return False, f"[WriteAction._validate] Acao não pode ter {' e '.join(self.allowed_fields)} ao mesmo tempo", None
        
        return True, None, present_fields.pop()
