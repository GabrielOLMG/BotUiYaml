import numpy as np
import cv2 
from rapidocr_onnxruntime import RapidOCR

rapid_ocr = RapidOCR(
    det_limit_side_len=960,  # mais parecido com o Spaces
    box_thresh=0.6,
    unclip_ratio=1.6,
    text_score=0.5,
    use_dilation=True,       # MUITO IMPORTANTE p/ colar caixas pequenas
    #rec_img_shape=[3, 48, 320]
)


def extract_base_text_info(image):
    results, _ = rapid_ocr(image)

    final_results = []

    for box, text, score in results:
        # Converte para numpy array
        pts = np.array(box, dtype=np.int32)
        x_min, y_min = pts[:, 0].min(), pts[:, 1].min()
        x_max, y_max = pts[:, 0].max(), pts[:, 1].max()

        # Calcula o centro da bbox
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        center = [center_x, center_y]

        final_results.append({
            "text": text,
            "score": float(score),
            "box": box,
            "center": center
        })

    return final_results


def find_text_in_image_rapidocr(image_path, text, threshold=0.8, contain=True, first=True, debug=False): # TODO: E se nao quiser o primeiro? 
    # TODO: Dividir a tela em 2 e tentar localizar, para poupar uso de memoria!
    try:
        image = cv2.imread(image_path)
        texts = extract_base_text_info(image)
        # text_flat = [t["text"] for t in texts]
        for texts_data in texts:
            text_extracted = texts_data["text"]
            center_extracted = texts_data["center"]
            confidence_extracted = texts_data["score"]

            if text in text_extracted and contain:
                if first:
                    return True, None, center_extracted
            elif text == text_extracted and not contain:
                if first:
                    return True, None, center_extracted
        return False, None, None 
    except Exception as err:
        return False, err, None
        # TODO: Esse log nao é de erro, deveria ser so o primeoro como False e o erro ser none, fazer try except p preencher esse log!
    