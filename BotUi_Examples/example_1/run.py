

from BotUi.BotUI import BotUI
from BotUi.classes.BotActions import BotActions
import logging
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')



if __name__ == "__main__":
    example_path = "BotUi_Examples/example_1"
    yaml_path = os.path.join(example_path ,"bot_yaml.yaml")
    output_path = os.path.join(example_path , "output")
    log_path = os.path.join(output_path, "example.log")

    os.makedirs(output_path, exist_ok=True)



    bot_ui = BotUI(
            yaml_path=yaml_path,
            log_file=log_path,
            log_level=logging.DEBUG,
            screenshots_path=output_path,
        )
    status = bot_ui.run()