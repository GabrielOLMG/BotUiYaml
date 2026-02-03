from BotUi.functions.utils import resolve_variables
from BotUi.classes.BotActionDispatcher import BotActionDispatcher


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
        # Exibe mensagem de ajuda, se houver
        helper_msg = step_info.get("helper")
        if helper_msg:
            self.bot_app.logger.info("🔹 Step: %s", helper_msg)

        # Inicializa dispatcher se ainda não estiver
        if not hasattr(self, "actions_dispatch"):
            self._init_actions_dispatch()

        # Resolve variaveis que ainda nao foram carregadas 
        resolved_step = self._resolve_step_vars(step_info)

        # Executa a ação via dispatcher
        action_completed, action_log = self.actions_dispatch.dispatch(resolved_step)

        if action_log:
            self.bot_app.logger.error("%s | Step Info: %s", action_log, resolved_step)

        # Retorna resultado da ação
        return action_completed, action_log



    # -----------------------
    # Helpers internos
    # -----------------------
    def _init_actions_dispatch(self):
        self.actions_dispatch = BotActionDispatcher(
            bot_driver=self.bot_driver,
            bot_app=self.bot_app,
        )

    def _resolve_step_vars(self, step_info):
        resolved = {}

        for key, value in step_info.items():
            resolved[key] = resolve_variables(value, self.bot_app.data_store, ignore_miss=False)

        return resolved