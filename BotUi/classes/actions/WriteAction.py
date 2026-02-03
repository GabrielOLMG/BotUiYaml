from BotUi.functions.utils import open_file
from BotUi.classes.abstracts.BaseAction import BaseAction



class WriteAction(BaseAction):
    def run(self):
        allowed_fields = {"text", "file_path"}
        present_fields = allowed_fields & self.step_info.keys()

        if not present_fields:
            return False, "WRITE requer 'text' ou 'file_path'"

        if len(present_fields) > 1:
            return False, f"WRITE não pode ter {' e '.join(list(allowed_fields))} ao mesmo tempo"

        field = present_fields.pop()
        value = self.step_info[field]
        if field == "file_path":
            value = open_file(value)
            
        executed, error = self.bot_driver.write(value)
        return executed, error