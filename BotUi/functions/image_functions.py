import cv2
import pytesseract
from difflib import SequenceMatcher
from PIL import Image
from functools import reduce
import numpy as np
from rapidocr_onnxruntime import RapidOCR

text_model = None
def get_text_detect_model():
    global text_model
    if not text_model:
        text_model = RapidOCR(
            det_limit_side_len=960,  # mais parecido com o Spaces
            box_thresh=0.6,
            unclip_ratio=1.6,
            text_score=0.5,
            use_dilation=True,       # MUITO IMPORTANTE p/ colar caixas pequenas
            #rec_img_shape=[3, 48, 320]
        )
        #text_model = RapidOCR(det_limit_side_len=500)
        # text_model = RapidOCR()

    return text_model

COLOR_DEFINITION = { # TODO: Melhor locel?
    "red": (
        [[0, 40, 50], [10, 255, 255]],
        [[170, 40, 50], [180, 255, 255]]
    ),
    "blue": ([[90, 70, 50], [130, 255, 255]], ),
    "black": ([[0, 0, 0], [180, 255, 80]], )
}

# def find_image_center(screenshot_path: str, template_path: str, threshold=0.9, try_gray_fallback=True):
#     """
#     Localiza o template na tela e retorna o centro (x, y) em pixels.
#     Agora suporta matching colorido (melhor para imagens com cores específicas).
#     return: 
#         Foi executado?, Erro?, Coord
#     """
#     # 1. Carrega em colorido (BGR padrão OpenCV)
#     screen_color = cv2.imread(screenshot_path)
#     template_color = cv2.imread(template_path)

#     if screen_color is None:
#         return False, f"Screenshot não encontrada em {screenshot_path}", None
#     if template_color is None:
#         return False, f"Template não encontrado em {template_path}", None

#     # 2. Faz matching colorido (usa todos os canais)
#     h, w = template_color.shape[:2]
#     res = cv2.matchTemplate(screen_color, template_color, cv2.TM_CCOEFF_NORMED)
#     _, max_val, _, max_loc = cv2.minMaxLoc(res)

#     # 3. Se não passou o threshold e try_gray_fallback=True, tenta em grayscale
#     if max_val < threshold and try_gray_fallback:
#         screen_gray = cv2.cvtColor(screen_color, cv2.COLOR_BGR2GRAY)
#         template_gray = cv2.cvtColor(template_color, cv2.COLOR_BGR2GRAY)
#         res = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
#         _, max_val, _, max_loc = cv2.minMaxLoc(res)

#     # 4. Retorna resultado se passou o threshold
#     if max_val < threshold:
#         return False, f"Não Foi Possivel Localizar a Image {template_path}", None

#     center_x = max_loc[0] + w // 2
#     center_y = max_loc[1] + h // 2
#     return True, None, (center_x, center_y)

def find_image_center_robust(screenshot_path: str, template_path: str, min_matches=10, scales=None):
    """
    Localiza o template na tela usando ORB feature matching e multi-scale.
    Retorna o centro (x, y) em pixels da área detectada.
    """
    screen = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    if screen is None:
        return False, f"Screenshot não encontrada em {screenshot_path}", None
    if template is None:
        return False, f"Template não encontrado em {template_path}", None

    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    template_gray_original = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # ORB detector
    orb = cv2.ORB_create(1000)

    kp_screen, des_screen = orb.detectAndCompute(screen_gray, None)
    if des_screen is None or len(kp_screen) == 0:
        return False, "Não foi possível detectar keypoints na screenshot.", None

    # Define escala para tentar múltiplos tamanhos do template
    if scales is None:
        scales = np.linspace(0.8, 1.2, 9)  # 80% a 120%

    best_center = None
    best_match_count = 0

    for scale in scales:
        w_scaled = int(template_gray_original.shape[1] * scale)
        h_scaled = int(template_gray_original.shape[0] * scale)
        if w_scaled < 10 or h_scaled < 10:
            continue  # ignora templates muito pequenos

        template_gray = cv2.resize(template_gray_original, (w_scaled, h_scaled))
        kp_template, des_template = orb.detectAndCompute(template_gray, None)
        if des_template is None or len(kp_template) == 0:
            continue

        # Matcher ORB
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des_template, des_screen)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) >= min_matches and len(matches) > best_match_count:
            best_match_count = len(matches)
            points = np.array([kp_screen[m.trainIdx].pt for m in matches])
            center_x = int(np.mean(points[:, 0]))
            center_y = int(np.mean(points[:, 1]))
            best_center = (center_x, center_y)

    if best_center is None:
        return False, f"Template não encontrado. Melhor match: {best_match_count} correspondências.", None

    return True, None, best_center

def preprocess_for_ocr(image):
    
    return image

def extract_base_text_info(image_path):
    ocr = get_text_detect_model()

    image = cv2.imread(image_path)
    image = preprocess_for_ocr(image)
    results, _ = ocr(image)

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

def encontrar_texto_central(image_path, text, threshold=0.8, contain_=True, first=True, debug=False): # TODO: E se nao quiser o primeiro? 
    # TODO: Dividir a tela em 2 e tentar localizar, para poupar uso de memoria!
    
    texts = extract_base_text_info(image_path)
    text_flat = [t["text"] for t in texts]
    if debug:
        print(text_flat)
    for texts_data in texts:
        text_extracted = texts_data["text"]
        center_extracted = texts_data["center"]
        confidence_extracted = texts_data["score"]

        if text in text_extracted and contain_:
            if first:
                return True, None, center_extracted
        elif text == text_extracted and not contain_:
            if first:
                return True, None, center_extracted



    return False, f"Não foi possivel Localizar o texto '{text}' na lista: {text_flat}", None

# def marcar_x_na_imagem(imagem_path, coordenada, output_path, tamanho=20, cor=(0, 0, 255), espessura=2): 
#     # Lê a imagem
#     img = cv2.imread(imagem_path)
#     if img is None:
#         raise FileNotFoundError(f"Imagem não encontrada: {imagem_path}")

#     x, y = coordenada
#     x = int(round(x))
#     y = int(round(y))
#     # Desenha o "X"
#     cv2.line(img, (x - tamanho, y - tamanho), (x + tamanho, y + tamanho), cor, espessura)
#     cv2.line(img, (x - tamanho, y + tamanho), (x + tamanho, y - tamanho), cor, espessura)

#     # Salva a imagem
#     cv2.imwrite(output_path, img)
#     return output_path, img


def marcar_x_na_imagem(
    imagem_path,
    coordenada,
    output_path,
    tamanho=30,
    espessura=2
):
    img = cv2.imread(imagem_path)
    if img is None:
        raise FileNotFoundError(f"Imagem não encontrada: {imagem_path}")

    x, y = map(int, coordenada)

    cor_marker = (0, 0, 255)
    cor_circulo = (0, 255, 255)

    # Marker
    cv2.drawMarker(
        img,
        (x, y),
        cor_marker,
        markerType=cv2.MARKER_CROSS,
        markerSize=tamanho,
        thickness=espessura
    )

    # Círculo
    cv2.circle(img, (x, y), tamanho, cor_circulo, espessura)

    # Texto com coordenadas
    texto = f"({x}, {y})"
    (w, h), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

    cv2.rectangle(
        img,
        (x + 10, y - h - 10),
        (x + 10 + w, y),
        (0, 0, 0),
        -1
    )
    cv2.putText(
        img,
        texto,
        (x + 10, y - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )

    cv2.imwrite(output_path, img)
    return output_path, img

def extract_text_from_image(image_file, color):
    """
    Extracts text from a pre-processed image using Tesseract OCR.
    """
    # Isolate the red text
    isolated_text_image = process_color_text_detection(image_file, color)
    if isolated_text_image is None:
        return False, "Extraction failed.", None
        
    try:
        # Use a page segmentation mode (PSM) that works well for a single line of text
        text = pytesseract.image_to_string(isolated_text_image)
        return True, None, text.strip()
    except pytesseract.TesseractNotFoundError:
        return False, "Tesseract was not found. Please check your installation and path settings.", None

def process_color_text_detection(image_path, color):
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


