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
        self.found = found
        self.center = center
        self.confidence = confidence
        self.debug_image = debug_image
        self.debug_image_path = debug_image

        self.message = log_message
