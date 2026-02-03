import cv2
import pytesseract
import numpy as np
from functools import reduce

from BotUi.classes.abstracts.BaseAction import BaseAction

COLOR_DEFINITION = {
    "red": (
        [[0, 40, 50], [10, 255, 255]],
        [[170, 40, 50], [180, 255, 255]]
    ),
    "blue": ([[90, 70, 50], [130, 255, 255]], ),
    "black": ([[0, 0, 0], [180, 255, 80]], )
}

class FindTextByColorAction(BaseAction):
    def run(self):
        color = self.step_info.get("color")
        save_as = self.step_info.get("save_as")

        screenshot_path, screenshot_image = self.capture()

        executed, error, output = self.extract_text_from_image(screenshot_path, color)

        if save_as and executed and error is None:
            self.set_var(save_as, output)

        log_text = f"[FIND_TEXT_BY_COLOR] {error} if error else None"

        return executed, log_text

    def extract_text_from_image(self, image_file, color):
        try:
            isolated_text_image = self.process_color_text_detection(image_file, color)
            if isolated_text_image is None:
                return False, "Falha na extração do texto.", None

            text = pytesseract.image_to_string(isolated_text_image)
            return True, None, text.strip()
        except pytesseract.TesseractNotFoundError:
            return False, "Tesseract não encontrado. Verifique a instalação.", None
        except Exception as e:
            return False, f"Erro durante OCR: {e}", None

    def process_color_text_detection(self, image_path, color):
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None

            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            masks = []

            for lower, upper in COLOR_DEFINITION[color]:
                lower = np.array(lower)
                upper = np.array(upper)
                masks.append(cv2.inRange(hsv, lower, upper))

            combined_mask = reduce(cv2.bitwise_or, masks)
            inverted_mask = cv2.bitwise_not(combined_mask)
            return inverted_mask
        except Exception as e:
            self.bot_app.logger.warning(f"[FIND_TEXT_BY_COLOR] Erro ao processar imagem: {e}")
            return None
