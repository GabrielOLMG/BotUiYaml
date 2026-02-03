import cv2
import pytesseract
import numpy as np

from functools import reduce

from BotUi.classes.abstracts.BaseAction import BaseAction


COLOR_DEFINITION = { # TODO: Melhor locel?
    "red": (
        [[0, 40, 50], [10, 255, 255]],
        [[170, 40, 50], [180, 255, 255]]
    ),
    "blue": ([[90, 70, 50], [130, 255, 255]], ),
    "black": ([[0, 0, 0], [180, 255, 80]], )
}

class FindTextByColorAction(BaseAction):
    def run(self):
        # --- (1) Captura configurações principais ---
        color = self.step_info.get("color")
        save_as = self.step_info.get("save_as")

        # --- (2) Screenshot ---
        screenshot_path, screenshot_image = self.capture()

        executed, error, output = self.extract_text_from_image(screenshot_path, color)

        if save_as and error is None:
            self.set_var(save_as, output)

        return executed, error
    
    # ----------------------
    # # Remover daqui?
    # ----------------------

    def extract_text_from_image(self, image_file, color):
        """
        Extracts text from a pre-processed image using Tesseract OCR.
        """
        # Isolate the red text
        isolated_text_image = self.process_color_text_detection(image_file, color)
        if isolated_text_image is None:
            return False, "Extraction failed.", None
            
        try:
            # Use a page segmentation mode (PSM) that works well for a single line of text
            text = pytesseract.image_to_string(isolated_text_image)
            return True, None, text.strip()
        except pytesseract.TesseractNotFoundError:
            return False, "Tesseract was not found. Please check your installation and path settings.", None
    
    def process_color_text_detection(self, image_path, color):
        image = cv2.imread(image_path)

        if image is None:
            print("Error: Image not found or could not be read.")
            return None

        # Convert the image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)   
        masks = []
        
        for lower, upper in COLOR_DEFINITION[color]:
            lower = np.array(lower)
            upper = np.array(upper)

            mask = cv2.inRange(hsv, lower, upper)
            masks.append(mask)
        
        combined_mask = reduce(cv2.bitwise_or, masks)
        inverted_mask = cv2.bitwise_not(combined_mask)

        return inverted_mask