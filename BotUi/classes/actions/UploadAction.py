from BotUi.functions.utils import parse_coord, check_path
from BotUi.classes.abstracts.BaseAction import BaseAction



class UploadAction(BaseAction):
    def run(self):
        raw_coord = self.step_info.get("coord")
        file_path = self.step_info["file_path"]

        coord = parse_coord(raw_coord)
        if coord is None:
            return False, "UPLOAD error reading upload coordination"

        if not check_path(file_path):
            return False, f"UPLOAD file {file_path} does not exist"

        executed, error = self.bot_driver.upload_file(file_path, coord)
        return executed, error