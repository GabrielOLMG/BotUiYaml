from BotUi.utils.utils import evaluate_condition
from BotUi.actions.abstracts.BaseAction import BaseAction



class DoWhileAction(BaseAction):
    def run(self):
        raise ValueError("EM MANUTENCAO!")
        # do_actions = self.step_info["do"]
        # while_condition_actions = self.step_info["while_condition"]
        # allowed_while_actions = ["FIND"]
        # keep_going = True

        # while keep_going:
        #     for i, do_action in enumerate(do_actions): # As Acoes Nao podem dar Erro
        #         print(f"fazendo action_{i}")
        #         actions = BotActions(
        #             bot_driver=self.bot_driver,
        #             bot_app=self.bot_app,
        #             step_info=do_action,
        #         )
        #         print(f"iniciando acao do Action_{i}")

        #         action_bool, action_error_log = actions.run_action()
        #         if not action_bool: 
        #             return action_bool, action_error_log

        #     for while_action in while_condition_actions: # O while por hora pode dar erro, so se 
        #         if while_action["action"] not in allowed_while_actions:
        #             return False, f"Atualmente o while pode apenas conter as acoes: {allowed_while_actions}"
        #         actions = BotActions(
        #             bot_driver=self.bot_driver,
        #             bot_app=self.bot_app,
        #             step_info=while_action,
        #         )
        #         while_bool, while_error_log = actions.run_action()
        #         if while_error_log: 
        #             return while_bool, while_error_log 
                
        #         if not while_bool: # TODO: Melhorar logica, pq por hora so funciina com FIND!
        #             keep_going = False
        #             break
        #         # TODO: Como que vou finalizar o while? nao posso permitir que finalize com erros
        #         # if not while_bool: 
        #         #     keep_going= False
        #         #     break
        # return True