import os
from typing import Optional, List, Dict, Literal, Any
from pydantic import BaseModel, model_validator, field_validator, RootModel


# ============================================================
# CONFIGURAÇÃO GLOBAL OPCIONAL
# ============================================================

class GlobalConfig(BaseModel):
    """Bloco opcional de configuração global."""
    variables: Optional[Dict[str, Any]] = None  # Ex: {"base_path": "/home/user", "lang": "pt"}


# ============================================================
# STEP E PIPELINE (seu código original)
# ============================================================

class Step(BaseModel):
    action: Literal[
        "WRITE", # README
        "KEYS_SELECTIONS", # README
        "RUN_SCRIPT",
        "FIND_TEXT_BY_COLOR",
        "STOP_IF",
        "FOR_EACH", # README
        "FIND", # README
        "DO_WHILE",
        "UPLOAD_FILE"
    ]

    '''
        FIND: Tem como objetivo localziar Imagem Ou Texto
        object_type: [img, text]
        if text:
            text
        if img:
            image_path
        click: Default False
        scrol_to_find: Default False
        if scrol_to_find:
            scroll_image_path
        direction: [UP, DOWN, AUTO(?)]
        x_coord
        y_coord
        '''

    # FIND ACTION
    object_type: Optional[Literal["IMG", "TEXT"]] = None
    text: Optional[str] = None
    image_path: Optional[str] = None
    click: Optional[bool] = False
    scroll: Optional[bool] = False
    scroll_image_path: Optional[str] = None
    scroll_direction: Optional[Literal["DOWN", "UP"]] = "DOWN" # TODO: Pensar em Algo como "auto"   
    x_coord: Optional[int] = 0
    y_coord: Optional[int] = 0
    in_text: Optional[bool] = True # Localiza texto igual ou contido. Se True, ele faz "text" in VALOR_ACHADOS caso contrario "text" == VALOR_ACHADOS 
    optional: Optional[bool] = False # Se é obrigatorio encontrar o objeto ou não, se True, ele avança para a proxima acao sem dar erro!
    debug: Optional[bool] = False
    until_find:  Optional[Literal["retry"]] = None
    if_find:  Optional[Literal["retry"]] = None


    # KEYS_SELECTIONS ACTION
    keys: Optional[List[str]] = None

    # WRITE ACTION
    file_path: Optional[str] = None

    # DO_WHILE ACTIONS # TODO!
    while_condition: Optional[List[Dict]] = None
    do: Optional[List[Dict]] = None

    # GLOBAL ACTIONS
    wait: Optional[float] = None
    helper: Optional[str] = None
    refresh: Optional[bool] = False
    save_url: Optional[str] = None # Ira salvar a url atual da pagina, que podera ser usado para fins do usuario


    coord: Optional[str] = None # Tornar obrigatorio para o upload?
    down: Optional[bool] = None
    save_as: Optional[str] = None
    color: Optional[str] = None
    script_path: Optional[str] = None
    condition: Optional[str] = None

    #global_allowed = ["wait", "helper", "refresh", "save_url"]

    def validate_find_action(self):
        allowed_field = ["object_type", "text", "image_path", "click",
                        "scroll", "scroll_image_path", "scroll_direction", # Transformar em um dicionario 
                        "x_coord", "y_coord",  # Transformar em um dicionario 
                        "in_text", "optional", "debug", "until_find", "if_find",
                        # Global
                        "wait", "helper", "refresh", "save_url"
                        ] 
        initial_error_text = "[ACTION FIND]"
        
        if not self.object_type:
            raise ValueError(f"{initial_error_text} The 'object_type' field is required.")
        if self.object_type == "IMG" and not self.image_path:
            raise ValueError(f"{initial_error_text} The 'object_type' as 'IMG' required 'image_path' field.")
        if self.object_type == "TEXT" and not self.text:
            raise ValueError(f"{initial_error_text} The 'object_type' as 'TEXT' required 'text' field")
        if self.scroll and not self.scroll_image_path:
            raise ValueError(f"{initial_error_text} To define the 'scroll' field, the 'scroll_image_path' field must be defined.")
        
    def validate_keys_selections(self):
        initial_error_text = "[ACTION KEYS_SELECTIONS]"

        if not self.keys:
            raise ValueError(f"{initial_error_text} The 'keys' field is required.")

    def validate_do_while(self):
        initial_error_text = "[ACTION DO_WHILE]"

        if not self.do:
            raise ValueError(f"{initial_error_text} The 'do' field is required.")
        if not self.while_condition:
            raise ValueError(f"{initial_error_text} The 'while_condition' field is required.")

    def validate_upload_file(self):
        initial_error_text = "[ACTION UPLOAD_FILE]"
        allowed_field = ["file_path", "coord"]

        if not self.file_path:
                raise ValueError(f" {initial_error_text} The 'file_path' field is required.")

    def validate_write(self):
        initial_error_text = "[ACTION WRITE]"
        allowed_field = ["text", "file_path"]


        if not self.text and not self.file_path:
            raise ValueError(f"{initial_error_text} The 'file_path' field or 'text' is required .")
        if self.text and self.file_path:
            raise ValueError(f"{initial_error_text} WRITE não pode ter text e file_path ao mesmo tempo")

    def validate_run_script(self):
        allowed_field = ["script_path"]

        if not self.script_path:
                raise ValueError("RUN_SCRIPT requer script_path")


    @model_validator(mode="after")
    def validate_fields(self):
        action = self.action

        if action == "FIND":
            self.validate_find_action()

        if action == "KEYS_SELECTIONS":
            self.validate_keys_selections()
        
        if action == "DO_WHILE":
            self.validate_do_while()

        if action == "UPLOAD_FILE":
            self.validate_upload_file()

        if action == "WRITE":
            self.validate_write()


        if action == "RUN_SCRIPT":
            self.validate_run_script()

        if action == "FIND_TEXT_BY_COLOR":
            if not self.color:
                raise ValueError("FIND_TEXT_BY_COLOR requer color")
            # if self.color not in COLOR_DEFINITION: # TODO: VOLTAR A APLICAR!
            #     raise ValueError(f"FIND_TEXT_BY_COLOR color '{self.color}' not found")

        if action == "STOP_IF" and not self.condition:
            raise ValueError("STOP_IF requer condition")

        if self.wait is not None and self.wait < 0:
            raise ValueError("wait deve ser >= 0")

        return self


class Pipeline(BaseModel):
    url: Optional[str] = None
    steps: List[Step]

    @field_validator("steps")
    @classmethod
    def validate_steps_not_empty(cls, v):
        if not v:
            raise ValueError("Cada pipeline deve conter pelo menos um passo")
        return v


# ============================================================
# MODELO FINAL QUE UNE CONFIG + PIPELINES
# ============================================================

class PipelineConfig(BaseModel):
    """Modelo raiz que suporta config + pipelines."""
    config: Optional[GlobalConfig] = None
    pipelines: Dict[str, Pipeline]

    @model_validator(mode="after")
    def validate_unique_pipeline_names(self):
        data = self.pipelines
        if len(data) != len(set(data.keys())):
            raise ValueError("Nomes de pipelines duplicados detectados")
        return self
