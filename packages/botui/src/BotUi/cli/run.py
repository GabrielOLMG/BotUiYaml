import json
import typer
from pathlib import Path

from BotUi.core.BotUIApp import BotUIApp

app = typer.Typer()


@app.command()
def start_bot(
    pipeline: str = typer.Option(...),
    bot: str = typer.Option(...),
    bot_variables: str | None = typer.Option(None),
    debug: bool = typer.Option(False)
):
    pipeline_path = Path(pipeline).resolve()

    if not pipeline_path.is_dir():
        raise typer.BadParameter("Pipeline path does not exist or is not a directory")

    yaml_path = (pipeline_path / bot).resolve()

    if not yaml_path.is_file():
        raise typer.BadParameter(f"Bot file not found: {bot}")

    output_folder = pipeline_path / "outputs"

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
        global_yaml_path=yaml_variables,
        debug_mode=debug
    )

    bot_ui.run()

@app.command()
def ocr_test(
    image_path: str = typer.Option(...),
    text_target: str | None = typer.Option(None),
):
    try: 
        from BotUi.finders.text.TextExtractor import TextExtractor
        
        extractor = TextExtractor(model_type="rapid_ocr", save_debug_internal=False)

        data = extractor.run(image_path, text_target)

        output = {
            "success": True,
            "result": data.to_dict(),
            "error": None
        }
    except Exception as err:
        import traceback
        tb = traceback.format_exc()
        output = {
            "success": False,
            "result": None,
            "error": f"{str(err)} -> {tb}"
        }

    typer.echo(json.dumps(output))


if __name__ == "__main__":
    app()