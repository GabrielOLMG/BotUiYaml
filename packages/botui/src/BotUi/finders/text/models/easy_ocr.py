class EasyOCRService:
    _ocr = None

    @classmethod
    def _get_model(cls):
        if cls._ocr is None:
            import easyocr

            cls._ocr = easyocr.Reader(['en'], gpu=False)
        return cls._ocr
    
    @classmethod
    def run(cls, image):
        model = cls._get_model()
        output = model.readtext(image, width_ths=0.5)

        if not output:
            return []

        return [
            {
                "box": box,
                "text": text,
                "score": score
            }
            for box, text, score in output
        ]