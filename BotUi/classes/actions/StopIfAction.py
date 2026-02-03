from BotUi.functions.utils import evaluate_condition
from BotUi.classes.abstracts.BaseAction import BaseAction



class StopIfAction(BaseAction):
    def run(self):
        executed, error, output = evaluate_condition(self.step_info["condition"])
        if not error and output:
            return False, f"Condition To Stop True: {self.step_info['condition']}=={output}"
        
        return executed, error