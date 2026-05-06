import os
import re
import ast
import yaml
import json
import uuid
import random

from copy import deepcopy
from BotUi.utils.utils import resolve_variables

class BotYamlExpander:
    def __init__(self, logger, main_yaml, global_yaml, bot_container_path):
        self.logger = logger
        self.data_store = {}
        self.main_yaml = main_yaml
        self.global_yaml = global_yaml
        self.bot_container_path = bot_container_path

    # -----------------------
    # Main functions
    # -----------------------
    def run(self):
        if not self.initialize_global_yaml(): return None, None
        if not self.initialize_main_yaml(): return None, None

        self.logger.info(f"Starting Yaml Expansion")
        pipeline = self.main_yaml.get("pipelines", {})

        for pipeline_name, pipeline_infos in pipeline.items():
            self.logger.debug(f"Preprocessing Pipeline {pipeline_name}")
            
            # URL
            if "url" in pipeline_infos:
                pipeline_infos["url"] = resolve_variables(
                    pipeline_infos["url"], self.data_store
                )

            # Steps
            if "steps" in pipeline_infos:
                pipeline_infos["steps"] = self.expand_step(
                    pipeline_infos["steps"]
                )
                for step in pipeline_infos["steps"]:
                    for key in step:
                        val = step[key]
                        val = resolve_variables(val, self.data_store)
                        step[key] = self._resolve_special_keys(val)

        return self.main_yaml, self.data_store
    
    def initialize_global_yaml(self):
        if not self.global_yaml:
            return True

        # Verifica se esta no formato correto # TODO: Fazer uma validacao por classe!
        global_yaml_config = self.global_yaml.get("config", None)
        if not global_yaml_config: 
            self.logger.error("❌ Global Configuration Yaml must be structured with 'Config'")
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
    # Expand functions
    # -----------------------
    def expand_step(self, steps: list):
        expanded_steps = []
        for step in steps:
            if step.get("action") == "FOR_EACH":
                expanded_steps.extend(self._expand_for_each_step(step))

            elif step.get("action") == "IMPORT_ACTIONS":
                expanded_steps.extend(self._expand_imported_action(step))
            else:
                # 🔁 verifica se há FOR_EACH dentro de steps aninhados
                if "steps" in step and isinstance(step["steps"], list):
                    step["steps"] = self._expand_for_each_step(step["steps"])
                expanded_steps.append(step)
        return expanded_steps
    
    def _expand_for_each_step(self, step):
        loop_var = step.get("loop_var")
        items = step.get("items", [])
        inner_steps = step.get("steps", [])

        if not loop_var:
            raise ValueError("FOR_EACH requer o campo 'loop_var'")
        if not inner_steps or not isinstance(inner_steps, list):
            raise ValueError("FOR_EACH requer 'steps' como lista de ações internas")

        if isinstance(items, str) and "$" in items:
            items = resolve_variables(items, self.data_store)
        if isinstance(items, str):
            try:
                items = ast.literal_eval(items)
            except Exception:
                raise ValueError(f"Não foi possível interpretar 'items': {items}")

        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
            print(items)
            raise ValueError(f"'items' deve ser uma lista de dicionários, recebido: {type(items)}")
        
        resolved_inner_steps = self.expand_step(inner_steps)
        expanded_steps = []
        for item in items:
            for inner_step in resolved_inner_steps:
                new_step = deepcopy(inner_step)
                serialized = json.dumps(new_step)
                for key, val in item.items():
                    pattern = rf"\{{\s*{loop_var}\.{key}\s*\}}"
                    serialized = re.sub(pattern, str(val), serialized)
                step_obj = json.loads(serialized)
                expanded_steps.append(step_obj)

        return self.expand_step(expanded_steps)
    
    def _expand_imported_action(self, step):
        if step.get("action") != "IMPORT_ACTIONS":
            return step
        
        import_path = f"{self.bot_container_path}/{step.get('path')}"
        if not import_path:
            raise ValueError("IMPORT_ACTIONS requer o campo 'path'")

        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_content = yaml.safe_load(f)
        except Exception as e:
            raise FileNotFoundError(f"Erro ao carregar YAML importado em '{import_path}': {e}")

        if not isinstance(import_content, list):
            raise ValueError(f"O arquivo importado '{import_path}' deve conter uma lista de ações, mas recebeu {type(import_content)}")

        return self.expand_step(import_content)

    def _expand_reference(self, depth=0):
        if depth > 10:
            self.logger.error("Maximum recursion reached in variables. Check circular references in YAML.")
            return

        has_remaining = False
        for variable_name, variable_value in self.data_store.items():
            if isinstance(variable_value, str) and "$" in variable_value:
                new_value = resolve_variables(variable_value, self.data_store)
                if new_value != variable_value:
                    self.data_store[variable_name] = new_value
                    has_remaining = True
        
        if has_remaining:
            self._expand_reference(depth + 1)

    # -----------------------
    # Others functions
    # -----------------------

    
    def _initialize_yaml_config(self, config):
        variables = config["variables"]
        has_reference = False
        for variable_name, variable_value in variables.items():
            if "$" in variable_value:
                has_reference = True
            if variable_name in self.data_store:
                return False, f" You cannot repeat configuration variables! '{variable_name}'"
            variable_value = self._resolve_special_keys(variable_value)
            self.data_store[variable_name] = variable_value

        if has_reference:
            self._expand_reference()

        return True, None
    
    # -----------------------
    # Special Keys functions
    # -----------------------
    def _resolve_special_keys(self, value):
        if not isinstance(value, str):
            return value
        
        value = self._load_file_sp(value)

        if "{{RANDOM_ID}}" in value:
            value = value.replace("{{RANDOM_ID}}", str(uuid.uuid4()))

        value = self._random_choice_sp(value)
        
        return value
    
    def _load_file_sp(self, value):
        if not isinstance(value, str):
            return value
        load_pattern = r"\{\{LOAD_FILE\.(.*?)\}\}"
        load_matches = re.findall(load_pattern, value)

        for file_path in load_matches:
            full_path = os.path.join(self.bot_container_path, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                if value == f"{{{{LOAD_FILE.{file_path}}}}}":
                    return content
                
                value = value.replace(f"{{{{LOAD_FILE.{file_path}}}}}", str(content))
            except Exception as e:
                self.logger.error(f"Erro ao carregar arquivo em {full_path}: {e}")
        return value


    def _random_choice_sp(self, value):
        if not isinstance(value, str):
            return value
        
        pattern = r"\{\{RANDOM_CHOICE\.(.*?)\}\}"
        matches = re.findall(pattern, value)

        for list_key in matches:
            choices_list = self.data_store.get(list_key)

            if isinstance(choices_list, list) and len(choices_list) > 0:
                choice = str(random.choice(choices_list))
                tag_to_replace = "{{" + f"RANDOM_CHOICE.{list_key}" + "}}"
                value = value.replace(tag_to_replace, choice)
            else:
                self.logger.warning(f"[BotYamlExpander._random_choice_sp] List key '{list_key}' not found or empty in data_store.")
        return value