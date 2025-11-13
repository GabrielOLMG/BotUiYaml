

from BotUi.BotUI import BotUI
from BotUi.classes.BotActions import BotActions

import logging

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def process_yaml(general_yamls_path, yamls_path):
    for general_yaml_file_name in general_yaml_files_name:
        yamls_path.append(os.path.join(general_yamls_path, f"{general_yaml_file_name}.yaml"))

    for yaml_bot in yamls_path:
        bot_ui = BotUI(
            yaml_path=yaml_bot,
            global_yaml_path=init_confg,
            log_file=log_path,
            log_level=logging.DEBUG,
            screenshots_path=screenshot_path,
        )
        status = bot_ui.run()
        if not status:
            break


if __name__ == "__main__":
    # ---------------------------------------------#
    # Mudar Para Cada Projeto/Maquina
    PROJECT_NAME = "SpaceFlightFlow" # "GlaucomaFlow" "DigitsFlow"
    MACHINE = "b8-85-84-c4-47-c9"
    # ---------------------------------------------#
    # ---------------------------------------------#
    # ---------------------------------------------#
    # ---------------------------------------------#
    # Não Mudar!
    project_path = f"projects_examples/Projects/{PROJECT_NAME}"
    general_yamls_path = f"projects_examples/General_Yamls/{MACHINE}"
    log_path = f"projects_examples/_output/{PROJECT_NAME}.log"
    init_confg = f"{project_path}/{PROJECT_NAME}_{MACHINE}.yaml"
    screenshot_path = "projects_examples/_output"
    # ---------------------------------------------#
    # ---------------------------------------------#
    # ---------------------------------------------#
    # ---------------------------------------------#
    # Alterar Se Precisar Escolher Qual Yaml Correr!
    yamls_path = []
    # general_yaml_files_name = ["1_create_project", "2_create_datasets", "3_create_modules", "4_create_experiment", "5_create_run", "6_create_deploy", "7_create_inference"]
    general_yaml_files_name = ["1_create_project", "2_create_datasets"]
    # ---------------------------------------------#
    # ---------------------------------------------#
    # ---------------------------------------------#
    # ---------------------------------------------#
    # Não Alterar Mais Nada
    process_yaml(general_yamls_path, yamls_path)
    # ---------------------------------------------#