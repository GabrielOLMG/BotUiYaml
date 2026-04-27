import os
import cv2
import json

from BotUi.finders.BotTargetResult import BotTargetResult

class BotTargetLocator:
    DETECTOR_TYPES = {
            "IMG": {"required": {"template_path"}, "function": "image_target_center"},
            "TEXT": {"required": {"target_text"}, "function": "text_target_center"}
        }
    
    def __init__(
            self,
            image_source_path:str, 
            debug_folder:str, 
            logger, 
            debug: bool = False, 
            offset_x:float=0, 
            offset_y:float=0
        ):
        self.image_source_path = image_source_path
        self.debug = debug
        self.logger = logger
        self.debug_folder = debug_folder # Mudar depois para ser algo mais unico, uma pasta com prints de debug,
        self.target_original_center = None
        self.target_shif_center = None

        self.offset_x = offset_x
        self.offset_y = offset_y

        self.shifted = False




    
    # ------------------------------------ #
    # Image 
    # ------------------------------------ #
    def image_target_center(
            self, 
            template_path: str, 
            debug:bool=False,
        ):
        from BotUi.finders.image import find_image_center_match_template, find_image_center_sift
        approaches_functions = [find_image_center_match_template, find_image_center_sift]
        image_source = cv2.imread(self.image_source_path, 0)
        template = cv2.imread(template_path, 0)

        for approach_function in approaches_functions:
            target_result = approach_function(image_source, template)

            if target_result.found:
                break
        
        return target_result
    
    
    # ------------------------------------ #
    # Text
    # ------------------------------------ #
    def text_target_center(
            self,
            target_text: str,
            in_text: bool = True,
            debug:bool=False,
            position:int=0,
            side:str=None
        ):
        from BotUi.finders.text.TextExtractor import TextExtractor

        models = ["rapid_ocr"]

        external_settings = {
            "position": position,
            "in_text": in_text,
        }
        for model in models:
            text_extractor = TextExtractor(model_type=model, **external_settings)
            target_result = text_extractor.run(image_path=self.image_source_path, text_target=target_text)
            if target_result.found:
                break

        return target_result
    
    # ------------------------------------ #
    # Others
    # ------------------------------------ #

    def _validate_kwargs(self, kwargs, required):
        missing = required - kwargs.keys()
        if missing:
            return False, f"Missing required args: {missing}"
        return True, None
    
    def debug_mark_shift(
        self,
        img,
        marker_size: int = 20,
        thickness: int = 2,
    ):
        x_orig, y_orig = map(int, self.target_original_center)
        x_shift, y_shift = map(int, self.target_shif_center)

        # Se a coordenada mudou, desenha uma seta
        if (x_orig, y_orig) != (x_shift, y_shift):
            cv2.arrowedLine(
                img,
                (x_orig, y_orig),
                (x_shift, y_shift),
                color=(255, 0, 0),  # amarelo
                thickness=thickness,
                tipLength=0.2
            )

        # Coloca label com coordenada
        texto = f"({x_shift}, {y_shift})"
        (w, h), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(
            img,
            (x_shift + 5, y_shift - h - 5),
            (x_shift + 5 + w, y_shift),
            (0, 0, 0),
            -1
        )
        cv2.putText(
            img,
            texto,
            (x_shift + 5, y_shift - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        return img

    def shift_coord(self):
        if self.target_original_center and (self.offset_x or self.offset_y):
            self.shifted = True
            return (self.target_original_center[0] + self.offset_x, self.target_original_center[1] + self.offset_y)
        else:
            return self.target_original_center

    # def _debug(self, debug_image = None):
    def _debug(self, target_result):
        if not self.debug:
            return target_result 
        
        if target_result.debug_json is not None:
            target_result.debug_json_path = os.path.join(self.debug_folder, "debug.json")
            
            # Save Json Here
            with open(target_result.debug_json_path, "w", encoding="utf-8") as f:
                json.dump(target_result.debug_json, f, indent=4, ensure_ascii=False)
        
        if target_result.debug_image is not None:
            if self.shift_coord:
                target_result.debug_image = self.debug_mark_shift(target_result.debug_image)
            target_result.debug_image_path = os.path.join(self.debug_folder, "debug.png")

            cv2.imwrite(target_result.debug_image_path, target_result.debug_image)
            
        return target_result


    # ------------------------------------ #
    # Dealer Functions
    # ------------------------------------ #
    def dealer(self, detector_type: str, **kwargs)-> 'BotTargetResult':
        if detector_type not in self.DETECTOR_TYPES:
            return BotTargetResult(error=True, log_message=f"Invalid detector_type: {detector_type}")
        
        config = self.DETECTOR_TYPES[detector_type]

        valid, error = self._validate_kwargs(kwargs, config["required"])
        if not valid:
            return BotTargetResult(error=True, log_message=error)

        detector_function = getattr(self, config["function"])
        kwargs["debug"]=self.debug
        target_result = detector_function(**kwargs)

        # TODO: Melhorar esta parte!
        self.target_original_center = target_result.center
        self.target_shif_center = self.shift_coord()
        target_result.center = self.target_shif_center

        if not target_result.error:
            target_result = self._debug(target_result)

        
        return target_result
    