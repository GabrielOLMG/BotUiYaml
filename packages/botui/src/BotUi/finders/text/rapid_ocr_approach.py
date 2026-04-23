import numpy as np
import cv2 

from BotUi.finders.BotTargetResult import BotTargetResult

class OCRService:
    def __init__(self):
        self._ocr = None

    def get(self):
        if self._ocr is None:
            from rapidocr_onnxruntime import RapidOCR

            self._ocr = RapidOCR(
                det_limit_side_len=960, # mais parecido com o Spaces
                box_thresh=0.6,
                unclip_ratio=1.6,
                text_score=0.5,
                use_dilation=True, # MUITO IMPORTANTE p/ colar caixas pequenas
            )
        return self._ocr



def extract_base_text_info(image):
    results, _ = OCRService().get()(image)

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

def split_image_half(image):
    """
    Por hora Apenas em 2!
    """
    _, w, _ = image.shape
    images = {
        "LEFT": image[:, :w//2],
        "RIGHT": image[:, w//2:]
    }

    return images

def same_detection(a, b, dist=20):
    return (
        a["text"] == b["text"] and
        abs(a["center"][0] - b["center"][0]) < dist and
        abs(a["center"][1] - b["center"][1]) < dist
    )

def merge_candidates(*lists):
    merged = []

    for candidates in lists:
        for c in candidates:
            found = False
            for i, m in enumerate(merged):
                if same_detection(c, m):
                    # mantém o de maior confidence
                    if c["confidence_extracted"] > m["confidence_extracted"]:
                        merged[i] = c
                    found = True
                    break

            if not found:
                merged.append(c)

    return merged


def find_text_in_image_rapidocr(image_path, text_target, in_text=True, side=None, debug=True, position=0):
    """
    Encontra texto em uma imagem usando RapidOCR, dividindo a imagem em LEFT, RIGHT e FULL para aumentar acurácia.
    
    Args:
        image_path: str, caminho da imagem
        text_target: str, texto a ser localizado
        in_text: bool, se True, considera matches que contêm o texto_target
        side: 'LEFT' ou 'RIGHT', caso queira buscar apenas em uma metade
        debug: bool, se True desenha caixas e confidence na imagem
        position: int, qual ocorrência usar se houver múltiplos matches (0 = maior confidence)
    
    Returns:
        tuple: (success: bool, log_text: str|None, center: list[float, float]|None, debug_image|None)
    """
    try:
        original_image = cv2.imread(image_path)
        if original_image is None:
            return BotTargetResult(error=True, log_message=f"Falha ao ler a imagem: {image_path}")

        h, w, _ = original_image.shape
        images_parts = split_image_half(original_image)

        # validação do parâmetro side
        if side and side.upper() not in ["LEFT", "RIGHT"]:
            return BotTargetResult(error=True, log_message=f"Opção de lado inválida: {side}")
        elif side:
            # remove a outra metade
            images_parts.pop(list({"LEFT", "RIGHT"} - {side.upper()})[0])
        else:
            # adiciona FULL para considerar toda a imagem
            images_parts["FULL"] = original_image

        texts = {}
        dict_debug = {}
        for side_name, image in images_parts.items():
            try:
                texts_extracted_data = extract_base_text_info(image)
                clean_data = [
                    {k: v for k, v in d.items() if k != "box"}
                    for d in texts_extracted_data
                ]
                dict_debug[side_name] = clean_data
            except Exception as e:
                return BotTargetResult(error=True, log_message=f"Erro ao extrair texto da imagem ({side_name}): {e}")

            possibles = []
            for text_extracted_data in texts_extracted_data:
                text_extracted = text_extracted_data["text"].strip()
                confidence_extracted = text_extracted_data["score"]
                center_extracted = text_extracted_data["center"]

                x_offset = 0
                if side_name == "RIGHT":
                    x_offset = w // 2
                center_extracted = [
                    center_extracted[0] + x_offset,
                    center_extracted[1]
                ]
                box = np.array(text_extracted_data["box"], dtype=np.int32)
                box[:, 0] += x_offset

                # aplica filtro
                if (in_text and text_target in text_extracted) or (not in_text and text_target == text_extracted):
                    possibles.append({
                        "text": text_extracted,
                        "confidence_extracted": confidence_extracted,
                        "center": center_extracted,
                        "box": box
                    })
            texts[side_name] = possibles

        # merge e ordenação final
        final_candidates = merge_candidates(
            texts.get("LEFT", []),
            texts.get("RIGHT", []),
            texts.get("FULL", [])
        )
        final_candidates = sorted(
            final_candidates,
            key=lambda c: (
                c["center"][1],         # cy top → bottom
                c["center"][0],         # cx left → right
                -c["confidence_extracted"]  # maior confidence primeiro
            )
        )

        # debug overlay
        debug_image = None
        if debug:
            debug_image = original_image.copy()
            for index, c in enumerate(final_candidates):
                box = np.array(c["box"], dtype=np.int32)
                cx, cy = map(int, c["center"])

                cv2.polylines(debug_image, [box], True, (0, 255, 0), 2)
                cv2.putText(
                    debug_image,
                    f"[{index}] {c['confidence_extracted']*100:.2f}%",
                    (cx, cy - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2
                )

        if len(final_candidates) == 0:
            return BotTargetResult(error=False, log_message=f"Nao foi possivel encontrar o texto desejado", debug_json=dict_debug)
        elif position > len(final_candidates):
            return BotTargetResult(error=True, log_message=f"Existem {len(final_candidates)} candidatos, mas foi passado position={position}, posiçao invalida", debug_json=dict_debug)


        final_candidate = final_candidates[position]
        return BotTargetResult(error=False, found=True, center=final_candidate["center"], debug_image=debug_image, confidence=final_candidate["confidence_extracted"], debug_json=dict_debug)

    except Exception as e:
        # catch geral com log completo
        return BotTargetResult(error=True, log_message=f"Erro inesperado ao localizar texto '{text_target}' em {image_path}: {e}")