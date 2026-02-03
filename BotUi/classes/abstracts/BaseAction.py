from abc import ABC, abstractmethod

class BaseAction(ABC):
    def __init__(self, bot_driver, bot_app, step_info):
        self.bot_driver = bot_driver
        self.bot_app = bot_app
        self.step_info = step_info

    @abstractmethod
    def run(self) -> tuple[bool, str | None]:
        pass

    # ------------------
    # Helpers comuns
    # ------------------
    def capture(self, label="screenshot") -> tuple[bool, str | None]:
        return self.bot_app.media_manager.capture(label)
    
    def set_var(self, key, value):
        self.bot_app.set_variable(key, value)

    def get_logger(self):
        return self.bot_app.logger