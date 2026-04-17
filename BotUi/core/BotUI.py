from BotUi.core.components import Pipeline
from BotUi.utils.utils import resolve_variables
from BotUi.core.BotActionDispatcher import BotActionDispatcher


class BotUI:

    def __init__(self, bot_app, bot_driver):
        # App (config, logger, yaml processado, data_store)
        self.bot_app = bot_app

        # Driver
        self.bot_driver = bot_driver

    # -----------------------
    # Main
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
        self.bot_app.logger.info("🔄 Executando pipelines")

        pipelines = self.bot_app.processed_yaml["pipelines"]
        self.actions_dispatch = BotActionDispatcher(
            bot_driver=self.bot_driver,
            bot_app=self.bot_app,
        )


        for pipeline_name, pipeline_infos in pipelines.items():
            pipeline = Pipeline(
                name=pipeline_name,
                pipeline_raw=pipeline_infos,
                bot_app=self.bot_app,
                bot_driver=self.bot_driver,
            )
            
            pipeline_result = pipeline.run(self.actions_dispatch)

            if pipeline_result.failed():
                return False

        self.bot_app.logger.info("✅ Todas as pipelines concluídas")
        return True
