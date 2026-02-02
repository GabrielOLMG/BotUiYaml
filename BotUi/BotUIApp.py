import os
import cv2
import logging
import numpy as np
import re
import ast
import json
from copy import deepcopy
import yaml


from PIL import Image
from io import BytesIO
from pydantic import ValidationError

from BotUi.BotUI import BotUI
from BotUi.classes.BotValidation import PipelineConfig
from BotUi.functions.utils import open_yaml, resolve_variables


class BotUIApp:
    def __init__(
            self,
            yaml_path: str,
            output_folder: str,
            global_yaml_path:str=None, 
            screenshot_folder:str=None,
            log_folder:str=None,
            debug_folder:str=None
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
        self.log_path = os.path.join(self.log_folder, "BotUI.log")
        self.screenshot_path = os.path.join(self.screenshot_folder, "screenshot_page.png")
        self.debug_path = os.path.join(self.debug_folder, "debug.png")
        self.yaml_processed_path = os.path.join(self.output_folder, "expanded_yaml.yaml")


        # 4) Others
        self.data_store = {}


    # -----------------------
    # Main # TODO: Colocar os devidos LOGs
    # -----------------------
    def run(self):
        # 0) Inicia Logger
        self.setup_logger()
        
        # 1) Valida Configuracao
        validated = self.validate_config()
        if not validated:
            return False
        
        # 2) Inicializa Yaml Global
        initialized = self.initialize_global_yaml()
        if not initialized:
            return False

        # 3) Inicializa Yaml Main
        initialized = self.initialize_main_yaml()
        if not initialized:
            return False
        
        # 4) Pre Processa o Yaml 
        self.processed_yaml = self._pre_process_main_yaml()
        self._save_preprocessed_yaml()

        

        # 5) Run BotUI
        bot_ui = BotUI(bot_app=self)
        status = bot_ui.run()

        # 6) Cria Midia Final!


    # -----------------------
    # Pipeline
    # -----------------------
    def setup_logger(self, log_level=logging.INFO):
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

    def initialize_global_yaml(self):
        if not self.global_yaml:
            return True

        # Verifica se esta no formato correto # TODO: Fazer uma validacao por classe!
        global_yaml_config = self.global_yaml.get("config", None)
        if not global_yaml_config: 
            self.logger.error("❌ Yaml de Configuracao Global deve estar estruturado com 'Config'") 
            return False

        # Inicializa Variaveis Globais
        initialized, error = self._initialize_yaml_config(global_yaml_config)
        if not initialized:
            self.logger.error(error)
            return False

        return True
    
    def initialize_main_yaml(self):
        main_yaml_config = self.main_yaml.get("config")
        if not main_yaml_config: 
            return True 
        
        # Inicializa Variaveis Main
        initialized, error = self._initialize_yaml_config(main_yaml_config)
        if not initialized:
            self.logger.error(error)
            return False

        return True

    # -----------------------
    # Setters
    # -----------------------
    def set_variable(self, key: str, value): # TODO: USAR ESTA FUNÇAO!
        self.data_store[key] = value

    # -----------------------
    # Others
    # -----------------------
    def _pre_process_main_yaml(self):
        self.logger.info(f"Iniciando Pre Processamento do Yaml")
        
        pipeline = self.main_yaml.get("pipelines", {})

        for pipeline_name, pipeline_infos in pipeline.items():
            # URL
            if "url" in pipeline_infos:
                pipeline_infos["url"] = resolve_variables(
                    pipeline_infos["url"], self.data_store
                )

            # Steps
            if "steps" in pipeline_infos:
                pipeline_infos["steps"] = self.expand_for_each(
                    pipeline_infos["steps"]
                )
            for step in pipeline_infos["steps"]:
                for key_name, raw_value in step.items():
                    step[key_name] = resolve_variables(raw_value, self.data_store)

        return self.main_yaml
        
    def _save_preprocessed_yaml(self):
        with open(self.yaml_processed_path, "w") as f:
            yaml.dump(self.processed_yaml, f, allow_unicode=True, sort_keys=False)

        self.logger.info(f"Novo Yaml Gerado Em '{self.yaml_processed_path}'")
        


    # -----------------------
    # Helpers ( Tentar Generalizar para remover daqui)
    # -----------------------

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






    # def _create_final_media(self, output_format="gif", fps=5):
    #     frames = []
    #     # 1️⃣ Normaliza tudo para PIL.Image (RGB)
    #     for screenshot in self.screenshots_history:

    #         if isinstance(screenshot, (bytes, bytearray)):
    #             img = Image.open(BytesIO(screenshot)).convert("RGB")

    #         elif isinstance(screenshot, np.ndarray):
    #             img = Image.fromarray(
    #                 cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    #             )

    #         else:
    #             raise TypeError(
    #                 f"Tipo de screenshot não suportado: {type(screenshot)}"
    #             )

    #         frames.append(img)

    #     if not frames:
    #         return

    #     # 2️⃣ Decide formato de saída
    #     if output_format == "gif":
    #         output_path = os.path.join(self.screenshots_path, "media.gif")

    #         frames[0].save(
    #             output_path,
    #             format="GIF",
    #             save_all=True,
    #             append_images=frames[1:],
    #             duration=int(1000 / fps),
    #             loop=0
    #         )

    #     elif output_format == "mp4":
    #         output_path = os.path.join(self.screenshots_path, "media.mp4")

    #         # PIL -> OpenCV
    #         frame_np = np.array(frames[0])
    #         height, width, _ = frame_np.shape

    #         fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    #         video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    #         for frame in frames:
    #             video.write(
    #                 cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
    #             )

    #         video.release()

    #     else:
    #         raise ValueError("output_format deve ser 'gif' ou 'mp4'")
    #     return output_path



    def _expand_reference(self):
        for variable_name, variable_value in self.data_store.items():
            if "$" in variable_value:
                self.data_store[variable_name] = resolve_variables(variable_value, self.data_store)
                self._expand_reference() # caso um $ chame outro $ que chama outro $


    def _initialize_yaml_config(self, config):
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
            self._expand_reference()

        return True, None