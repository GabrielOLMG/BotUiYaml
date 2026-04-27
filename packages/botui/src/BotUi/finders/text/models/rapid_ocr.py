class RapidOCRService:
    def __init__(self):
        self._ocr = None

    def _get_model(self):
        if self._ocr is None:
            from rapidocr_onnxruntime import RapidOCR

            self._ocr = RapidOCR(
                det_limit_side_len=300,
                box_thresh=0.6,
                unclip_ratio=1.6,
                text_score=0.5,
                use_dilation=True,
            )
        return self._ocr

    def run(self, image):
        model = self._get_model()
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