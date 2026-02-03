from BotUi.functions.utils import parse_coord, check_path
from BotUi.classes.abstracts.BaseAction import BaseAction



class UploadAction(BaseAction):
    def run(self):
        validated, log_text, (coord, file_path) =  self._validate()
        if not validated:
            return False, log_text
        
        executed, result_log = self.bot_driver.upload_file(file_path, coord)

        return executed, result_log

    def _validate(self):
        raw_coord = self.step_info.get("coord")
        file_path = self.step_info["file_path"]

        coord = parse_coord(raw_coord)
        if coord is None:
            return False, "[UPLOAD] Coordenadas inválidas ou não informadas", (None, None) 
        
        if not check_path(file_path):
            return False, f"[UPLOAD] Arquivo não existe: {file_path}", (None, None)
        
        return True, None, (coord, file_path)