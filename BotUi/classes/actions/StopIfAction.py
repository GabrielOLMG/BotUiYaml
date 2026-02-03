from BotUi.functions.utils import evaluate_condition
from BotUi.classes.abstracts.BaseAction import BaseAction



class StopIfAction(BaseAction):
    def run(self):
        executed, error, output = evaluate_condition(self.step_info["condition"])

        # Se a condição retornar True, queremos parar o pipeline
        if not error and output:
            return False, f"[STOP_IF] Condição para parar satisfeita: {self.step_info['condition']} == {output}"

        # Retorna sucesso ou log do erro
        result_log = None
        if error:
            result_log = f"[STOP_IF] Erro ao avaliar condição: {error}"

        return executed, result_log
