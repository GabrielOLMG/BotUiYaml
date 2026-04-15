import os
from pathlib import Path
from pydantic import BaseModel, Field, model_validator

class RunBotRequest(BaseModel):
    pipeline_dir: str = Field(
        ...,
        description="Absolute path to the folder containing necessary information about the bot.",
        example="/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/BotUi_Examples"
    )

    bot_relative_path: str = Field(
        ...,
        description="The bot's YAML relative path, which must be contained within the *pipeline_dir*.",
        example="example_fun_1/bot_yaml.yaml <I.E> /Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/BotUi_Examples/example_fun_1/bot_yaml.yaml"
    )

    globals_relative_path: str = Field(
        ...,
        description="Relative path to the bot global configuration file inside the *pipeline directory*.",
        example="example_fun_1/bot_yaml.yaml <I.E> /Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/BotUi_Examples/example_fun_1/bot_variables.yaml"
    )
    
    @model_validator(mode="after")
    def validate_paths(self):
        pipeline = Path(self.pipeline_dir).resolve()

        if not pipeline.is_dir():
            raise ValueError(f"Directory '{pipeline}' does not exist.")

        # -------------------------
        # BOT FILE
        # -------------------------
        bot = (pipeline / self.bot_relative_path).resolve()

        if pipeline not in bot.parents:
            raise ValueError("bot_relative_path must be inside pipeline_dir.")

        if not bot.is_file():
            raise ValueError(
                f"Bot file '{self.bot_relative_path}' not found inside '{pipeline}'."
            )

        if bot.suffix not in [".yaml", ".yml"]:
            raise ValueError("Bot file must be a YAML file.")

        # -------------------------
        # GLOBALS FILE
        # -------------------------
        globals_path = (pipeline / self.globals_relative_path).resolve()

        if pipeline not in globals_path.parents:
            raise ValueError("globals_relative_path must be inside pipeline_dir.")

        if not globals_path.is_file():
            raise ValueError(
                f"Globals file '{self.globals_relative_path}' not found inside '{pipeline}'."
            )

        if globals_path.suffix not in [".yaml", ".yml"]:
            raise ValueError("Globals file must be a YAML file.")

        return self