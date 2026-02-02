import re
import ast
import cv2
import time
import json
import logging
import numpy as np


from PIL import Image
from io import BytesIO
from copy import deepcopy
from pydantic import ValidationError


from .functions.utils import *
from .functions.image_functions import *


from .classes.BotValidation import *
from .classes.BotActions import BotActions
from .classes.drivers.PlaywrightDriver import PlaywrightDriver


class BotUI:
    """
    BotUI: Framework para automação de UI via YAML.
    - Valida YAML usando Pydantic
    - Coordena pipelines e steps
    - Executa ações via Selenium
    - Logging profissional com níveis, cores e arquivo
    """
    DEFAULT_DRIVER = PlaywrightDriver
    def __init__(
            self,
            yaml_path: str,
            screenshots_path:str,
            global_yaml_path: str | None = None,  # TODO: Melhorar o nome!
            log_file: str | None = None,
            log_level=logging.INFO,
    ):
        # Tipo de driver que sera usado
        self.bot_driver = self.DEFAULT_DRIVER()
        

        # Configuração
        self.yaml_conf = open_yaml(yaml_path)        
        self.data_store = {}
        self.actions = None  
        self.screenshots_path = screenshots_path
        self.screenshots_history = []
        self.global_yaml_path = global_yaml_path


        # Logger
        self.logger = self._setup_logger(log_file, log_level)

    def init_global_vars(self): # TODO: Fazer Verificação para esse arquivo!
        if self.global_yaml_path:
            yaml_data = open_yaml(self.global_yaml_path)["config"]
            return self.init_config(yaml_data)
        return True, None

    def init_actions(self, step_info):
        self.actions = BotActions(
            bot_driver=self.bot_driver,
            data_store=self.data_store,
            logger=self.logger,
            step_info=step_info,
            screenshots_path=self.screenshots_path
        )
    
    def expand_conf(self):
        for variable_name, variable_value in self.data_store.items():
            if "$" in variable_value:
                self.data_store[variable_name] = resolve_variables(variable_value, self.data_store)
                self.expand_conf() # caso um $ chame outro $ que chama outro $

    def init_config(self, config):
        variables = config["variables"]
        has_reference = False
        for variable_name, variable_value in variables.items():
            if "$" in variable_value:
                has_reference = True
            if variable_name in self.data_store:
                return False, f" Não Pode Repetir Variaveis! '{variable_name}'"
            self.data_store[variable_name] = variable_value

        # Verifica se Variaveis de Configuração chamam a propria variavel de configuração        
        if has_reference:
            self.expand_conf()
        


        return True, None

    def _expand_action(self, step):
        loop_var = step.get("loop_var")
        items = step.get("items", [])
        inner_steps = step.get("steps", [])

        if not loop_var:
            raise ValueError("FOR_EACH requer o campo 'loop_var'")
        if not inner_steps or not isinstance(inner_steps, list):
            raise ValueError("FOR_EACH requer 'steps' como lista de ações internas")

        # 🔹 Resolve variáveis dinâmicas
        if isinstance(items, str) and "$" in items:
            items = resolve_variables(items, self.data_store)
        if isinstance(items, str):
            try:
                items = ast.literal_eval(items)
            except Exception:
                raise ValueError(f"Não foi possível interpretar 'items': {items}")

        # 🔹 Garante lista de dicts
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
            print(items)
            raise ValueError(f"'items' deve ser uma lista de dicionários, recebido: {type(items)}")

        expanded_steps = []
        for item in items:
            for inner_step in inner_steps:
                new_step = deepcopy(inner_step)
                serialized = json.dumps(new_step)
                for key, val in item.items():
                    pattern = rf"\{{\s*{loop_var}\.{key}\s*\}}"
                    serialized = re.sub(pattern, str(val), serialized)
                step_obj = json.loads(serialized)

                # 🔁 Se o step expandido ainda tiver FOR_EACH dentro, processa recursivamente
                if step_obj.get("action") == "FOR_EACH":
                    expanded_steps.extend(self._expand_action(step_obj))
                else:
                    expanded_steps.append(step_obj)

        return expanded_steps

    def expand_for_each(self, steps: list):
        expanded_steps = []
        for step in steps:
            if step.get("action") == "FOR_EACH":
                expanded_steps.extend(self._expand_action(step))
            else:
                # 🔁 verifica se há FOR_EACH dentro de steps aninhados
                if "steps" in step and isinstance(step["steps"], list):
                    step["steps"] = self.expand_for_each(step["steps"])
                expanded_steps.append(step)
        return expanded_steps

    # -----------------------
    # Logging
    # -----------------------
    def _setup_logger(self, log_file: str | None, log_level: int) -> logging.Logger:
        logger = logging.getLogger("BotUI")
        logger.setLevel(log_level)

        # Formatter com cores no terminal
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler opcional
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger

    # -----------------------
    # Validação do YAML
    # -----------------------
    def validate_config(self) -> bool:
        try:
            PipelineConfig.model_validate(self.yaml_conf).model_dump()
            self.logger.info("✅ YAML válido!")
            return True
        except ValidationError as e:
            self.logger.error("❌ Erros de validação do YAML:\n%s", e)
            return False

    # -----------------------
    # Execução principal
    # -----------------------
    def run(self) -> bool:
        validated = self.validate_config()

        # TODO: Melhorar essa parte! INICIO
        status, error = self.init_global_vars()

        if not status:
            self.logger.exception(f"❌ Erro inesperado durante execução: {error}")
            return False
        if "config" in self.yaml_conf:
            status, error = self.init_config(self.yaml_conf["config"])
            if not status:
                self.logger.exception(f"❌ Erro inesperado durante execução: {error}")
                return False
        # TODO: Melhorar essa parte! FIM

        if not validated:
            return False

        self.logger.info("🔄 Iniciando execução de pipelines")

        status = self.process_pipelines()
        self.logger.info("🧹 Finalizando e encerrando o driver...")
        self.bot_driver.close()

        return status

    def process_pipelines(self) -> bool:
        pipeline = self.yaml_conf["pipelines"]

        for pipeline_name, pipeline_infos in pipeline.items():
            status = self.process_pipeline(pipeline_name, pipeline_infos)
            if not status:
                return False
        self.logger.info("✅ Todas as pipelines concluídas")
        return True

    def process_pipeline(self, pipeline_name: str, pipeline_infos: dict):
        url = pipeline_infos.get("url")
        if url and "$" in url: # TODO: Melhorar! GENERALIZAR PARA TODO O CODIGO
            url = resolve_variables(url, self.data_store)

        steps = self.expand_for_each(pipeline_infos["steps"])
        # TODO: Fazer check se prmieria pipeline tem url!

        if url:
            status = self.bot_driver.goto(url)
            if status:
                self.logger.info("🚀 Pipeline '%s' iniciada na URL: %s", pipeline_name, url)
            else:
                self.logger.error("❌ Erro ao iniciar Pipeline '%s' na URL: %s", pipeline_name, url)
                return False

        # Executa os steps definidos
        for step in steps:
            step_completed, _ = self.run_step(step)
            if not step_completed:
                return False
        
        self._create_final_media()

        return True

    def run_step(self, step_info: dict): 
        helper_msg = step_info.get("helper")
        if helper_msg:
            self.logger.info("🔹 Step: %s", helper_msg)

        self.init_actions(step_info)
        
        action_completed, action_log = self.actions.run_action() 
        self.screenshots_history.extend(self.actions.screenshots_action_history)

        if action_log is not None:
            self.logger.error(f"{action_log} | Step Info: {step_info}")


        return action_completed, action_log

    # -----------------------
    # Funções auxiliares
    # -----------------------
    def _create_final_media(self, output_format="gif", fps=5):
        frames = []
        # 1️⃣ Normaliza tudo para PIL.Image (RGB)
        for screenshot in self.screenshots_history:

            if isinstance(screenshot, (bytes, bytearray)):
                img = Image.open(BytesIO(screenshot)).convert("RGB")

            elif isinstance(screenshot, np.ndarray):
                img = Image.fromarray(
                    cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
                )

            else:
                raise TypeError(
                    f"Tipo de screenshot não suportado: {type(screenshot)}"
                )

            frames.append(img)

        if not frames:
            return

        # 2️⃣ Decide formato de saída
        if output_format == "gif":
            output_path = os.path.join(self.screenshots_path, "media.gif")

            frames[0].save(
                output_path,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=int(1000 / fps),
                loop=0
            )

        elif output_format == "mp4":
            output_path = os.path.join(self.screenshots_path, "media.mp4")

            # PIL -> OpenCV
            frame_np = np.array(frames[0])
            height, width, _ = frame_np.shape

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            for frame in frames:
                video.write(
                    cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                )

            video.release()

        else:
            raise ValueError("output_format deve ser 'gif' ou 'mp4'")
        return output_path
