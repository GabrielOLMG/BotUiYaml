from BotUi.utils.utils import check_path, run_script
from BotUi.actions.abstracts import BaseAction, BaseActionResult



class RunScriptAction(BaseAction):
    def run(self):
        script_path = self.step_info.get("script_path")
        flags = self.step_info.get("flags")
        save_as = self.step_info.get("save_as")

        # Validação inicial
        if not check_path(script_path):
            return BaseActionResult(
                    finished=False,
                    success=False,
                    message=f"[RunScriptAction.run] Arquivo não encontrado: {script_path}"
                )

        executed, error, output = run_script(script_path, flags)

        # Salvar output se necessário
        if save_as and error is None:
            self.set_var(save_as, output)

        return BaseActionResult(
                        finished=not error,
                        success=executed,
                        message=f"[RunScriptAction.run] Erro ao executar script: {error}" if error else None
                    )
