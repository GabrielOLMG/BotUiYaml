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


# ---------------------- #
def get_magnitude(image):
    """
    Calculates the gradient magnitude of an image using OpenCV Sobel filters.
    image: grayscale image (2D)
    Returns: gradient magnitude (float32)
    """
    # Sobel on X axis (horizontal)
    gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
    
    # Sobel on Y axis (vertical)
    gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)

    # Gradient magnitude
    magnitude = cv2.magnitude(gx, gy)

    return magnitude

def get_bbox_coords(top_left, width, height):
    """
    Returns the top-left corner (given) and bottom-right corner (calculated).
    """
    x = top_left[0]
    y = top_left[1]
    bottom_right = (x + width, y + height)

    return top_left, bottom_right

def draw_bbox_image(image, top_left, bottom_right):
    image_copy = image.copy()
    if len(image_copy.shape) == 2:  # grayscale
        image_copy = cv2.cvtColor(image_copy, cv2.COLOR_GRAY2RGB)
    
    cv2.rectangle(image_copy, top_left, bottom_right, (255, 0, 0), 2)

    return image_copy

def get_crop_of_image(image, top_left, bottom_right):
    """
    Returns the region of the image defined by the rectangle from top_left to bottom_right.
    top_left and bottom_right: (x, y)
    """
    return image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

def normalized_correlation(template, crop):
    """
    Calculates the normalized correlation between a template and a cropped region.
    template, crop: same dimensions, float32 or float64
    Returns a value between 0 and 1.
    """
    # optionally flatten to 1D (not required)
    template_flat = template.flatten()
    crop_flat = crop.flatten()
    
    numerator = np.sum(template_flat * crop_flat)
    denominator = np.sqrt(np.sum(template_flat**2) * np.sum(crop_flat**2))
    
    if denominator == 0:
        return 0.0  # avoid division by zero
    return numerator / denominator

def get_bbox_center(top_left, bottom_right):
    """
    Returns the center (x, y) of a bounding box.
    """
    center_x = top_left[0] + (bottom_right[0] - top_left[0]) // 2
    center_y = top_left[1] + (bottom_right[1] - top_left[1]) // 2
    return (center_x, center_y)


def find_image_center(image_source_path: str, template_path: str, threshold=0.95):
    # Open Images
    image_source = cv2.imread(image_source_path,0)
    template = cv2.imread(template_path, 0)

    # Original Magnitude
    source_magnitude = get_magnitude(image_source)
    template_magnitude = get_magnitude(template)

    # Normalized Cross Correlation (faster using cv2!) (TM_CCORR_NORMED makes it normalized!)
    correlated_matrix_norm = cv2.matchTemplate(
        source_magnitude.astype(np.float32),
        template_magnitude.astype(np.float32),
        cv2.TM_CCORR_NORMED
    )

    # Get coordinates with value above the threshold
    indices = np.where(correlated_matrix_norm >= threshold)

    # Organize into coordinates
    rows, cols = indices
    coords = [(col, row) for row, col in zip(rows, cols)]  # Format as (x, y) where x is column and y is row

    # Select the candidate with the highest similarity
    image_with_bbox = None
    center = None

    for coord in coords:
        template_width = template.shape[1]
        template_height = template.shape[0]

        # Get the coordinates of the image crop
        top_left, bottom_right = get_bbox_coords(coord, template_width, template_height)
        image_cropped = get_crop_of_image(image_source, top_left, bottom_right)

        # Crop Magnitude
        magnitude_crop = get_magnitude(image_cropped)

        # Cosine similarity
        score = normalized_correlation(template_magnitude, magnitude_crop)

        if score >= 0.95:  # TODO: Another param? Could stop at 0.95, else continue searching
            image_with_bbox = draw_bbox_image(image_source, top_left, bottom_right)
            center = get_bbox_center(top_left, bottom_right)
            break
        elif score >= 0.8:
            # Not sure if is correct
            image_with_bbox = draw_bbox_image(image_source, top_left, bottom_right)
            center = get_bbox_center(top_left, bottom_right)


    if image_with_bbox is not None:
        return True, None, center
    else:
        return True, "No match found!", center


