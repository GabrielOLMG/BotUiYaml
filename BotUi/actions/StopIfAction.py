from BotUi.utils.utils import evaluate_condition
from BotUi.actions.abstracts import BaseAction, BaseActionResult



class StopIfAction(BaseAction):
    def run(self):
        executed, error, output = evaluate_condition(self.step_info["condition"])

        # Se a condição retornar True, queremos parar o pipeline
        if not error and output:
            return BaseActionResult(
                finished=False,
                success=True,
                message=f"[StopIfAction.run] Condição para parar satisfeita: {self.step_info['condition']} == {output}"
            )

        return BaseActionResult(
                finished=not error,
                success=executed,
                message=f"[StopIfAction.run] Erro ao avaliar condição: {error}" if error else None
            )
