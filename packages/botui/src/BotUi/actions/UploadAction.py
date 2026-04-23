from BotUi.utils.utils import parse_coord, check_path
from BotUi.actions.abstracts import BaseAction, BaseActionResult



class UploadAction(BaseAction):
    def run(self):
        validated, log_text, (coord, file_path) =  self._validate()
        if not validated:
            return BaseActionResult(
                finished=False,
                success=False,
                message=log_text
            )
        
        executed, log_text = self.bot_driver.upload_file(file_path, coord)

        return BaseActionResult(
                    finished=True,
                    success=executed,
                    message=f"[UploadAction.run] {log_text}" if log_text else None
                )

    def _validate(self):
        raw_coord = self.step_info.get("coord")
        file_path = self.step_info["file_path"]

        coord = parse_coord(raw_coord)
        if coord is None:
            return False, f"[UploadAction._validate] Coordenadas inválidas ou não informadas: coord='{coord}'", (None, None) 
        
        if not check_path(file_path):
            return False, f"[UploadAction._validate] Arquivo não existe: {file_path}", (None, None)
        
        return True, None, (coord, file_path)