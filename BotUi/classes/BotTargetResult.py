class BotTargetResult:
    def __init__(
        self,
        error: bool,
        
        found: bool=False,
        center=None,

        confidence: float = None,
        debug_image=None,
        debug_image_path=None,
        log_message: str = "",
    ):
        self.error = error
        self.log_message = log_message


        self.center = center
        self.found = found
        self.confidence = confidence

        self.debug_image = debug_image
        self.debug_image_path = debug_image_path

