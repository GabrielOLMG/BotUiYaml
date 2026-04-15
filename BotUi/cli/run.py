import typer
from pathlib import Path

from BotUi.core.BotUIApp import BotUIApp

app = typer.Typer()


@app.command()
def run(
    pipeline: str = typer.Option(...),
    bot: str = typer.Option(...),
    bot_variables: str | None = typer.Option(None)
):
    pipeline_path = Path(pipeline).resolve()

    if not pipeline_path.is_dir():
        raise typer.BadParameter("Pipeline path does not exist or is not a directory")

    yaml_path = (pipeline_path / bot).resolve()

    if not yaml_path.is_file():
        raise typer.BadParameter(f"Bot file not found: {bot}")

    output_folder = yaml_path.parent / "output"

    yaml_variables = None
    if bot_variables:
        yaml_variables_path = (pipeline_path / bot_variables).resolve()

        if yaml_variables_path.exists():
            yaml_variables = str(yaml_variables_path)
        else:
            raise typer.BadParameter(f"Variables file not found: {bot_variables}")

    bot_ui = BotUIApp(
        yaml_path=str(yaml_path),
        output_folder=str(output_folder),
        global_yaml_path=yaml_variables
    )

    bot_ui.run()


if __name__ == "__main__":
    app()