import time
import logging
import cv2
import sys
import json
import re
import ast

from copy import deepcopy
from pydantic import ValidationError

from .functions.selenium_functions import *
from .functions.key_map import *
from .functions.utils import *
from .functions.image_functions import *
from .functions.tests import test_driver

from .classes.validation_models import *
from .classes.BotActions import BotActions

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver


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
            driver=None # Possibilidade de Enviar externamente o driver
    ):
        # Configuração
        self.yaml_conf = open_yaml(yaml_path)
        self.driver = driver
        self.data_store = {}
        self.actions = None  
        self.screenshots_path = screenshots_path
        self.global_yaml_path = global_yaml_path

        # Logger
        self.logger = self._setup_logger(log_file, log_level)

    def init_global_vars(self): # TODO: Fazer Verificação para esse arquivo!
        if self.global_yaml_path:
            yaml_data = open_yaml(self.global_yaml_path)["config"]
            return self.init_config(yaml_data)


    def init_actions(self, step_info):
        self.actions = BotActions(
            driver=self.driver,
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


    def _init_driver(self):
        """
        Obtém o driver Selenium.
        - Se nenhum driver foi passado pelo usuário, cria o padrão da biblioteca.
        - Se o usuário passou um driver, valida se ele está funcional.
        """
        if not self.driver:
            self.logger.info("🧩 Nenhum driver fornecido. Criando driver padrão da biblioteca...")
            try:
                self.driver = get_driver()

                if not test_driver(self.driver):
                    self.logger.error("❌ Driver padrão criado, mas falhou no teste de funcionalidade.")
                    return False
                self.logger.info("✅ Driver padrão criado e validado com sucesso.")
            except Exception as e:
                self.logger.exception(f"❌ Falha ao criar driver padrão: {e}")
                return False
        else:
            self.logger.info("🔌 Driver fornecido externamente. Validando funcionalidade...")
            try:
                if not test_driver(self.driver):
                    self.logger.error("❌ Driver fornecido não está funcional. Verifique configuração.")
                    return False
                self.logger.info("✅ Driver externo validado e funcional.")
            except Exception as e:
                self.logger.exception(f"❌ Erro ao validar driver fornecido: {e}")
                return False

        return True

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
            finish_driver(self.driver)

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

        if not self.driver:
            if not self._init_driver():
                return False

        if url:
            status = self._go_to_url(url)
            if status:
                self.logger.info("🚀 Pipeline '%s' iniciada na URL: %s", pipeline_name, url)
            else:
                self.logger.error("❌ Erro ao iniciar Pipeline '%s' na URL: %s", pipeline_name, url)

                return False
        elif not self.driver:
            self.logger.error("⚠️ Pipeline '%s' não define URL e nenhum driver foi inicializado.", pipeline_name)
            return False

        # Executa os steps definidos
        for step in steps:
            if not self.run_step(step):
                self.logger.error("❌ Step falhou na pipeline '%s'.", pipeline_name)
                return False

        return True

    # -----------------------
    # Execução de step
    # -----------------------
    def run_step(self, step_info: dict):
        helper_msg = step_info.get("helper")
        if helper_msg:
            self.logger.info("🔹 Step: %s", helper_msg)


        self.init_actions(step_info)
        action_bool, action_error_log = self.actions.run_action()

        if not action_bool:
            self.finish(action_error_log)
            return False
        return True

    # -----------------------
    # Funções auxiliares
    # -----------------------

    def _go_to_url(self, url: str, wait_time: float = 5.0) -> bool:
        try:
            self.driver.get(url)
            time.sleep(wait_time)
            return True
        except Exception as e:
            return False


    def finish(self, reason):
        self.logger.error(f"❌ {reason}")
        finish_driver(self.driver)

