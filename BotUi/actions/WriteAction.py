from BotUi.utils.utils import open_file
from BotUi.actions.abstracts.BaseAction import BaseAction



class WriteAction(BaseAction):
    def __init__(self, bot_driver, bot_app, step_info):
        super().__init__(bot_driver, bot_app, step_info)

        self.allowed_fields = ["text", "file_path"]

    def run(self):
        validated, log_text, field = self._validate()

        if not validated:
            return False, log_text

        value = self.step_info[field]
        if field == "file_path":
            value = open_file(value)
            
        success, result_log = self.bot_driver.write(value)

        return success, result_log

    def _validate(self):
        present_fields = set(self.allowed_fields) & self.step_info.keys()

        if not present_fields:
            return False, f"[WRITE] Acao Requer {' ou '.join(self.allowed_fields)}", None

        if len(present_fields) > 1:
            return False, f"[WRITE] Acao não pode ter {' e '.join(self.allowed_fields)} ao mesmo tempo", None
        
        return True, None, present_fields.pop()
