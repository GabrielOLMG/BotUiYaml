from pydantic import BaseModel, Field, model_validator


# =========================
# Payload Run
# =========================

class RunBotRequest(BaseModel):
    pipeline_dir: str = Field(
        ...,
        description="Absolute path to the folder containing necessary information about the bot.",
        example="/Users/BotUiYaml/BotPipelines"
    )

    bot_relative_path: str = Field(
        ...,
        description="The bot's YAML relative path, which must be contained within the *pipeline_dir*.",
        example="example_1/bot_yaml.yaml"
    )

    globals_relative_path: str = Field(
        default=None,
        description="Relative path to the bot global configuration file inside the *pipeline directory*.",
        example="example_1/bot_variables.yaml"
    )

    debug: bool = Field(
        default=False,
        description="",
    )

    n_instances: int = Field(
        default=1,
        description="",
    )
# =========================
# Payload Response
# =========================


class RunBotResponse(BaseModel):
    job_id: str = Field(
        ...,
        description="Unique ID for the run",
    )

    container_name: str = Field(
        ...,
        description="Name of the created container",
    )

    container_id: str = Field(
        ...,
        description="ID of the created container",
    )

    status: str = Field(
        ...,
        description="run status",
    )