from BotUi.core.components import Step
from BotUi.utils.utils import resolve_variables
from BotUi.core.BotActionDispatcher import BotActionDispatcher


class BotUI:

    def __init__(self, bot_app, bot_driver):
        # App (config, logger, yaml processado, data_store)
        self.bot_app = bot_app

        # Driver
        self.bot_driver = bot_driver

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
            self.bot_app.logger.info(f"🚀 Starting the Pipeline: {pipeline_name}")
            status = self._process_pipeline(pipeline_name, pipeline_infos)
            if not status:
                return False

        self.bot_app.logger.info("✅ Todas as pipelines concluídas")
        return True

    def _process_pipeline(self, pipeline_name: str, pipeline_infos: dict) -> bool:
        if not hasattr(self, "actions_dispatch"):
            self._init_actions_dispatch()

        url = pipeline_infos.get("url")
        if url and not self._start_pipeline(pipeline_name, url):
            return False
        
        steps = [
            Step(bot_app=self.bot_app, bot_driver=self.bot_driver, step_raw=step_info) 
            for step_info in pipeline_infos["steps"]
        ]

        for step in steps:
            step_result = step.run(self.actions_dispatch)
            
            if not step_result.success:
                return False

        return True

    def _start_pipeline(self, pipeline_name: str, url: str) -> bool:
        status = self.bot_driver.goto(url)

        if status:
            self.bot_app.logger.info(
                "Opening URL: %s",
                url,
            )
        else:
            self.bot_app.logger.error(
                "Error opening URL: %s",
                url,
            )

        return status

    # -----------------------
    # Helpers internos
    # -----------------------
    def _init_actions_dispatch(self):
        self.actions_dispatch = BotActionDispatcher(
            bot_driver=self.bot_driver,
            bot_app=self.bot_app,
        )
