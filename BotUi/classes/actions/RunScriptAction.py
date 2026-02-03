from BotUi.functions.utils import check_path, run_script
from BotUi.classes.abstracts.BaseAction import BaseAction



class RunScriptAction(BaseAction):
    def run(self):
        script_path, flags = self.step_info.get("script_path"), self.step_info.get("flags")
        save_as = self.step_info.get("save_as")
        
        if not check_path(script_path):
            return False, f"RUN_SCRIPT file {script_path} does not exist"

        executed, error, output = run_script(script_path, flags)

        if save_as and error is None:
            self.set_var(save_as, output)

        return executed, error