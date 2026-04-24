class BotTargetResult:
    def __init__(
        self,
        error: bool,
        
        target_type: str= None,
        found: bool=False,
        center=None,

        confidence: float = None,
        debug_image=None,
        debug_image_path=None,
        debug_json:dict=None,
        debug_json_path:dict=None,
        
        log_message: str = "",
    ):
        self.error = error
        self.log_message = log_message
        self.target_type = target_type



        self.center = center
        self.found = found
        self.confidence = confidence

        self.debug_image = debug_image
        self.debug_image_path = debug_image_path
        self.debug_json = debug_json
        self.debug_json_path = debug_json_path


