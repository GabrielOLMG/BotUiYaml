from BotUi.classes.abstracts.BaseAction import BaseAction


class KeySelectionsAction(BaseAction):
    def run(self):
        keys = self.step_info.get("keys")
        if not keys:
            return False, "[KEYS_SELECTIONS] Nenhuma tecla fornecida"

        executed, error = self.bot_driver.key_sequence(keys)

        log_text = f"[KEYS_SELECTIONS] Erro na execução da sequência: {error}" if error else None
        return executed, log_text
