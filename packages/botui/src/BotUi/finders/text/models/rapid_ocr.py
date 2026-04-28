class RapidOCRService:
    _ocr = None

    @classmethod
    def _get_model(cls):
        if cls._ocr is None:
            from rapidocr_onnxruntime import RapidOCR

            cls._ocr = RapidOCR(
                det_limit_side_len=960,
                box_thresh=0.5,
                unclip_ratio=1,      
                use_dilation=False,    
            )
        return cls._ocr

    @classmethod
    def run(cls, image):
        model = cls._get_model()
        output = model(image)

        if not output:
            return []

        results, _ = output 

        if not results:
            return []

        return [
            {
                "box": box,
                "text": text,
                "score": score
            }
            for box, text, score in results
        ]