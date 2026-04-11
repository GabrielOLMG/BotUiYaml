

from BotUi.BotUIApp import BotUIApp
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

EXAMPLE_PATH = "BotUi_Examples/"


def run_example(example_name="example_1"):
    example_folder = os.path.join(EXAMPLE_PATH, example_name)
    yaml_path = os.path.join(example_folder, "bot_yaml.yaml")
    output_folder = os.path.join(example_folder , "output")

    bot_ui = BotUIApp(
            yaml_path=yaml_path,
            output_folder=output_folder
        )

    status = bot_ui.run()


if __name__ == "__main__":
    run_example()