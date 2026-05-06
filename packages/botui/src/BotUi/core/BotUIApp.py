import os
import yaml
import logging

from pydantic import ValidationError

from BotUi.core.BotUI import BotUI
from BotUi.utils.utils import open_yaml
from BotUi.core.BotValidation import PipelineConfig
from BotUi.core.BotYamlExpander import BotYamlExpander 
from BotUi.media.BotMediaManager import BotMediaManager
from BotUi.drivers.PlaywrightDriver import PlaywrightDriver


class BotUIApp:
    DEFAULT_DRIVER = PlaywrightDriver

    def __init__(
            self,
            yaml_path: str,
            output_folder: str,
            bot_container_path: str,
            global_yaml_path:str=None, 
            screenshot_folder:str=None,
            log_folder:str=None,
            debug_folder:str=None,
            debug_mode=False,
        ):
        
        # 1) Carrega Yaml Principal 
        self.main_yaml = open_yaml(yaml_path)

        # 2) Carrega Yaml Global
        self.global_yaml = open_yaml(global_yaml_path) if global_yaml_path else None

        # 3) Output Folder & Screenshot Folder & Log Folder
        self.output_folder = output_folder
        self.debug_folder = debug_folder if debug_folder else os.path.join(self.output_folder, "debugs")
        self.screenshot_folder = screenshot_folder if screenshot_folder else os.path.join(self.output_folder, "screenshots")
        self.log_folder = log_folder if log_folder else os.path.join(self.output_folder, "logs")

        # 4) Cria Devidas Pastas, se nao existir
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.debug_folder, exist_ok=True)
        os.makedirs(self.screenshot_folder, exist_ok=True)
        os.makedirs(self.log_folder, exist_ok=True)

        # 5) Path
        self.bot_container_path = bot_container_path
        self.log_path = os.path.join(self.log_folder, "BotUI.log")
        self.screenshot_path = os.path.join(self.screenshot_folder, "screenshot_page.png")
        self.debug_path = os.path.join(self.debug_folder, "debug.png")
        self.yaml_processed_path = os.path.join(self.output_folder, "expanded_yaml.yaml")


        # 4) Others
        self.data_store = {}
        self.bot_driver = self.DEFAULT_DRIVER()
        self.debug_mode = debug_mode
        self.log_level = logging.DEBUG if self.debug_mode else logging.INFO 
        self.setup_logger()




    # -----------------------
    # Main # TODO: Colocar os devidos LOGs
    # -----------------------
    def run(self):
        try:
            if not self.validate_config(): return False
            
            yaml_expander = BotYamlExpander(
                logger=self.logger,
                main_yaml=self.main_yaml,
                global_yaml=self.global_yaml,
                bot_container_path=self.bot_container_path
            )
            self.processed_yaml, self.data_store = yaml_expander.run()
            if not self.processed_yaml:
                return False
            
            self._save_preprocessed_yaml() # TODO: FUNCAO UTILS AQUI!
            self.logger.info(f"Final YAML generated in: '{self.yaml_processed_path}'")

            # 5) Define Media Manager
            self.media_manager = BotMediaManager(
                bot_driver=self.bot_driver,
                output_path=self.screenshot_path,
                logger=self.logger
            )

            # 6) Run BotUI
            bot_ui = BotUI(
                bot_app=self,
                bot_driver=self.bot_driver,
                debug_mode=self.debug_mode
                )
            status = bot_ui.run()

            # 7) Cria Midia Final!
            self.media_manager.create_final_media(output_format="mp4")

            return status
        except Exception as err:
            import traceback
            tb = traceback.format_exc()
            self.logger.critical(f"Serious Failure {str(err)} -> {tb}", exc_info=True)
            return False
        finally:
            if hasattr(self, 'bot_driver'):
                self.bot_driver.close()



    # -----------------------
    # Pipeline
    # -----------------------
    def setup_logger(self):
        logger = logging.getLogger("BotUI")
        logger.setLevel(self.log_level)

        # Formatter com cores no terminal
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler opcional

        fh = logging.FileHandler(self.log_path)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        self.logger = logger

    def validate_config(self):
        try:
            PipelineConfig.model_validate(self.main_yaml).model_dump()
            self.logger.info("✅ YAML válido!")
            return True
        except ValidationError as e:
            self.logger.error("❌ Erros de validação do YAML:\n%s", e)
            return False

    # -----------------------
    # Setters
    # -----------------------
    def set_variable(self, key: str, value): # TODO: USAR ESTA FUNÇAO!
        self.data_store[key] = value

    # -----------------------
    # Others
    # -----------------------
    def _save_preprocessed_yaml(self): # TODO: Vira um utils!
        with open(self.yaml_processed_path, "w") as f:
            yaml.dump(self.processed_yaml, f, allow_unicode=True, sort_keys=False)

        
        