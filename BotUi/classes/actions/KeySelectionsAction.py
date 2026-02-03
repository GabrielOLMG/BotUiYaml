from BotUi.classes.abstracts.BaseAction import BaseAction


class KeySelectionsAction(BaseAction):
    def run(self):
        executed, error = self.bot_driver.key_sequence(self.step_info["keys"]) 
        return executed, error