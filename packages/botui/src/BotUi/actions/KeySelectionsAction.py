from BotUi.actions.abstracts import BaseAction, BaseActionResult


class KeySelectionsAction(BaseAction):
    def run(self):
        keys = self.step_info.get("keys")
        if not keys:
            return BaseActionResult(
                        finished=False,
                        success=False,
                        message="[KeySelectionsAction.run] Nenhuma tecla fornecida"
                    )

        executed, error = self.bot_driver.key_sequence(keys)

        return BaseActionResult(
                        finished=not error,
                        success=executed,
                        message=f"[KeySelectionsAction.run] Erro na execução da sequência: {error}" if error else None
                    )