from BotUi.BotUIApp import BotUIApp
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')



if __name__ == "__main__":
    example_path = "BotUi_Examples/example_1"
    yaml_path = os.path.join(example_path ,"bot_yaml.yaml")

    output_folder = os.path.join(example_path , "output")

    bot_ui = BotUIApp(
            yaml_path=yaml_path,
            output_folder=output_folder,
        )
    status = bot_ui.run()