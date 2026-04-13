

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
    yaml_variables = os.path.join(example_folder , "bot_variables.yaml")

    

    
    bot_ui = BotUIApp(
            yaml_path=yaml_path,
            output_folder=output_folder,
            global_yaml_path=yaml_variables if os.path.exists(yaml_variables) else None
        )

    status = bot_ui.run()


if __name__ == "__main__":
    example_name = "example_fun_1"
    if example_name:
        run_example(example_name)
    else: 
        run_example()