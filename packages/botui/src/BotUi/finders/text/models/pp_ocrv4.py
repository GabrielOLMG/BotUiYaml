class PaddleOCRV4:
    _ocr = None

    @classmethod
    def _get_model(cls):
        if PaddleOCRV4._ocr is None:
            from paddleocr import PaddleOCR

            PaddleOCRV4._ocr = PaddleOCR(
                ocr_version='PP-OCRv3', lang='en', use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False,  text_det_limit_side_len=768, text_det_thresh=0.5, text_det_box_thresh=0.8, text_det_unclip_ratio=1.0
                )

        return PaddleOCRV4._ocr

    @classmethod
    def run(cls, image):
        model = cls._get_model()
        output = model.predict(image)

        if not output:
            return []

        results = output[0] 

        if not results:
            return []

        return [
            {
                "box": box,
                "text": text,
                "score": score
            }
            for text, box, score in zip(results["rec_texts"], results["rec_polys"], results["rec_scores"])
        ]