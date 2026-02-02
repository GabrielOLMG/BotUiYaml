from BotUi.classes.BotActions import BotActions
from BotUi.classes.drivers.PlaywrightDriver import PlaywrightDriver


class BotUI:
    DEFAULT_DRIVER = PlaywrightDriver

    def __init__(self, bot_app):
        # App (config, logger, yaml processado, data_store)
        self.bot_app = bot_app

        # Driver
        self.bot_driver = self.DEFAULT_DRIVER()

        # Runtime state
        self.screenshots_history: list = []


    # -----------------------
    # API pública
    # -----------------------
    def run(self) -> bool:
        self.bot_app.logger.info("🚀 Iniciando BotUI")

        try:
            status = self._process_pipelines()
            return status
        finally:
            self.bot_app.logger.info("🧹 Finalizando driver")
            self.bot_driver.close()

    # -----------------------
    # Pipelines
    # -----------------------
    def _process_pipelines(self) -> bool:
        pipelines = self.bot_app.processed_yaml["pipelines"]

        self.bot_app.logger.info("🔄 Executando pipelines")

        for pipeline_name, pipeline_infos in pipelines.items():
            status = self._process_pipeline(pipeline_name, pipeline_infos)
            if not status:
                return False

        self.bot_app.logger.info("✅ Todas as pipelines concluídas")
        return True

    def _process_pipeline(self, pipeline_name: str, pipeline_infos: dict) -> bool:
        url = pipeline_infos.get("url")
        steps = pipeline_infos["steps"]

        if url and not self._start_pipeline(pipeline_name, url):
            return False

        for step in steps:
            step_completed, _ = self._run_step(step)
            if not step_completed:
                return False

        return True

    def _start_pipeline(self, pipeline_name: str, url: str) -> bool:
        status = self.bot_driver.goto(url)

        if status:
            self.bot_app.logger.info(
                "🚀 Pipeline '%s' iniciada na URL: %s",
                pipeline_name,
                url,
            )
        else:
            self.bot_app.logger.error(
                "❌ Falha ao iniciar Pipeline '%s' na URL: %s",
                pipeline_name,
                url,
            )

        return status

    # -----------------------
    # Steps
    # -----------------------

    def _run_step(self, step_info: dict):
        helper_msg = step_info.get("helper")
        if helper_msg:
            self.bot_app.logger.info("🔹 Step: %s", helper_msg)

        self._init_actions(step_info)

        action_completed, action_log = self.actions.run_action()
        self.screenshots_history.extend(self.actions.screenshots_action_history)

        if action_log:
            self.bot_app.logger.error(
                "%s | Step Info: %s",
                action_log,
                step_info,
            )

        return action_completed, action_log


    # -----------------------
    # Helpers internos
    # -----------------------
    def _init_actions(self, step_info: dict):
        self.actions = BotActions(
            bot_driver=self.bot_driver,
            bot_app=self.bot_app,
            step_info=step_info,
        )
