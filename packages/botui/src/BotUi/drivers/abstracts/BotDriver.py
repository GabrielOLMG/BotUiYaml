# classes/abstracts/bot_driver.py
from abc import ABC, abstractmethod

class BotDriver(ABC):
        
    # ---------------------- #
    # Actions
    # ---------------------- #
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def goto(self, url: str, wait_time: float):
        pass

    @abstractmethod
    def reload(self):
        pass
    
    @abstractmethod
    def click(self, coord: tuple, delay_ms:int):
        pass

    @abstractmethod
    def upload_file(self, file_path: str, coord:tuple):
        pass

    @abstractmethod
    def write(self, text):
        pass

    @abstractmethod
    def scroll(self, direction: str, delta_x: int, delta_y: int, coord: tuple):
        pass

    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def key_sequence(self, keys: list):
        pass
    
    # ---------------------- #
    # Gets
    # ---------------------- #
    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def get_screenshot(self, output_path) -> bytes:
        pass
