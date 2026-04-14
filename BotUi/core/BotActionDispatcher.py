import time
import requests

from BotUi.actions.WriteAction import WriteAction
from BotUi.actions.FindAction import FindAction
from BotUi.actions.KeySelectionsAction import KeySelectionsAction
from BotUi.actions.RunScriptAction import RunScriptAction
from BotUi.actions.FindTextByColorAction import FindTextByColorAction
from BotUi.actions.StopIfAction import StopIfAction
from BotUi.actions.UploadAction import UploadAction
from BotUi.actions.DoWhileAction import DoWhileAction



class BotActionDispatcher:
    ACTION_MAP = {
        "WRITE": WriteAction,
        "FIND": FindAction,
        "KEYS_SELECTIONS": KeySelectionsAction,
        "RUN_SCRIPT": RunScriptAction,
        "FIND_TEXT_BY_COLOR": FindTextByColorAction,
        "STOP_IF": StopIfAction,
        "UPLOAD_FILE": UploadAction,
        "DO_WHILE": DoWhileAction,
    }

    def __init__(self, bot_driver, bot_app):
        self.bot_app = bot_app
        self.bot_driver = bot_driver


    def dispatch(self, step_info) -> tuple[bool, str | None]:
        action_name = step_info.get("action")
        action_class = self.ACTION_MAP.get(action_name)

        if not action_class:
            return False, f"Ação não implementada: {action_name}"


        # Instancia a classe da ação correta
        action_instance = action_class(
            bot_driver=self.bot_driver,
            bot_app=self.bot_app,
            step_info=step_info
        )

        # Executa a ação
        task_completed, log_text =  action_instance.run()

        if log_text is not None and not task_completed: # TODO: Garantir que esta funcional com 'and'
            return False, log_text
        
        # Global Actions
        self._apply_global_step_behavior(step_info)

        

        if step_info.get("debug") is True:
            self.bot_app.logger.info("Pipeline Pausada Para Debug, va até http://localhost:8000/docs#/") # TODO: Redirecionar para a pagina que mostra a imagem de debug, ou dados de debug!

            response = requests.post("http://127.0.0.1:8000/debug/pause")

            # backend vai liberar aqui depois do /resume
            action = response.json().get("action")

            if action == "stop":
                return False, "Debug: execução interrompida pelo usuário"


        return task_completed, log_text
    
    def _apply_global_step_behavior(self, step_info):
        if step_info.get("refresh"):
            self.bot_driver.reload()
        if step_info.get("wait"):
            time.sleep(step_info["wait"])
        if step_info.get("save_url"):
            self.bot_app.set_variable(
                step_info["save_url"], self.bot_driver.get_url()
            )
        # Captura final
        self.bot_app.media_manager.capture("screenshot")




