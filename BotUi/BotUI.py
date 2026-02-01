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
from .functions.key_map import *
from .functions.image_functions import *
from .functions.playwright_functions import *


from .classes.BotValidation import *
from .classes.BotActions import BotActions

class BotUI:
    """
    BotUI: Framework para automação de UI via YAML.
    - Valida YAML usando Pydantic
    - Coordena pipelines e steps
    - Executa ações via Selenium
    - Logging profissional com níveis, cores e arquivo
    """

    def __init__(
            self,
            yaml_path: str,
            screenshots_path:str,
            global_yaml_path: str | None = None,  # TODO: Melhorar o nome!
            log_file: str | None = None,
            log_level=logging.INFO,
    ):
        # Configuração
        self.yaml_conf = open_yaml(yaml_path)
        self.page = None
        self.pw = None
        self.browser = None 
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
            page=self.page,
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

        try:
            status = self.process_pipelines()
        except Exception as e:
            self.logger.exception(f"❌ Erro inesperado durante execução: {e}")
            status = False
        finally:
            self.logger.info("🧹 Finalizando e encerrando o driver...")
            self._finish_page()

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

        if not self.pw:
            if not self._init_driver():
                return False

        if url:
            status = self._go_to_url(url)
            if status:
                self.logger.info("🚀 Pipeline '%s' iniciada na URL: %s", pipeline_name, url)
            else:
                self.logger.error("❌ Erro ao iniciar Pipeline '%s' na URL: %s", pipeline_name, url)

                return False
        elif not self.pw:
            self.logger.error("⚠️ Pipeline '%s' não define URL e nenhum driver foi inicializado.", pipeline_name)
            return False

        # Executa os steps definidos
        for step in steps:
            if not self.run_step(step):
                self.logger.error("❌ Step falhou na pipeline '%s'.", pipeline_name)
                return False
        
        self._create_final_media()

        return True

    # -----------------------
    # Execução de step
    # -----------------------
    def run_step(self, step_info: dict): # TODO: Mudar para retornar o erro!
        helper_msg = step_info.get("helper")
        if helper_msg:
            self.logger.info("🔹 Step: %s", helper_msg)


        self.init_actions(step_info)
        # TODO: O action bool deve ser revisto. para o find é se achou, mas para o resto é se deu erro, entao vou olhar apenas para op texto de erro se existe
        # o action bool deve ser algo como "finalizou a acao"
        action_done, action_error, screenshots_action_history = self.actions.run_action() 
        self.screenshots_history.extend(screenshots_action_history)

        if not action_done:
            self.finish(action_error)
            return False
        return True

    # -----------------------
    # Funções auxiliares
    # -----------------------
    def _init_driver(self):
        self.pw, self.browser, self.page = get_page()
        return True

    def _go_to_url(self, url: str, wait_time: float = 5.0) -> bool:
        try:
            self.page.goto(url, wait_until="networkidle")
            time.sleep(wait_time)
            return True
        except Exception as e:
            return False

    def _finish_page(self):
        finish_page(self.pw, self.browser)

    def finish(self, reason):
        self.logger.error(f"❌ {reason}")
        finish_page(self.pw, self.browser)

    # def _create_final_gif(self):
    #     git_output_path = os.path.join(self.screenshots_path, "final_gif.gif")

    #     self.logger.error("Criando GIF com o processo completo")
    #     frames = []

    #     for screenshot in self.screenshots_history:

    #         # Caso 1 — veio do Playwright (bytes)
    #         if isinstance(screenshot, (bytes, bytearray)):
    #             img = Image.open(BytesIO(screenshot)).convert("RGB")

    #         # Caso 2 — veio do OpenCV (numpy array BGR)
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

    #     frames[0].save(
    #         git_output_path,
    #         format="GIF",
    #         save_all=True,
    #         append_images=frames[1:],
    #         duration=300,
    #         loop=0
    #     )

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
