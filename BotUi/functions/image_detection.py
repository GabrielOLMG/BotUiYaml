import numpy as np
import cv2

# ------------------------------------ #
# SIFT + FLANN + RANSAC 
# ------------------------------------ #


def get_keypoints_descriptors(source_image, template_image, debug=False):
    sift = cv2.SIFT_create(
        contrastThreshold = 0.1 , # Filtra keypoints fracos
        nOctaveLayers = 13, # Quantidade de Octave
        edgeThreshold = 15, # Filtra keypoints fracos
        sigma = 1.0 # Blur inicial 
    )
    keypoints_source, descriptors_source = sift.detectAndCompute(source_image, None)
    keypoints_template, descriptors_template = sift.detectAndCompute(template_image, None)

    descriptors_source = descriptors_source.astype(np.float32)
    descriptors_template = descriptors_template.astype(np.float32)


    if debug:
        print(f"Total Source Keypoints: {len(keypoints_source)} || Total Template Keypoints: {len(keypoints_template)}")

    return (keypoints_source, descriptors_source), (keypoints_template, descriptors_template)


def get_flann_match(descriptors_source, descriptors_template):
    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(descriptors_template, descriptors_source, k=2)
    
    return matches

def ratio_test(matches):
    good_maches = []
    for m,n in matches:
        if m.distance < 0.6*n.distance:
            good_maches.append(m)

    return good_maches

def get_ransac_result(good_maches, keypoints_source, keypoints_template):
    src_pts = np.float32([keypoints_template[m.queryIdx].pt for m in good_maches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints_source[m.trainIdx].pt for m in good_maches]).reshape(-1, 1, 2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, maxIters=10000, ransacReprojThreshold=3.0) # ransacReprojThreshold: Quanto maior o valor, mais chance de achar alinhamentos falhos(Homografia pode “entortar”)

    matchesMask = mask.ravel().tolist() if mask is not None else None
    
    return matchesMask, mask, M

def get_draw_image(matches_mask, good_maches, source_image, template_image, keypoints_source, keypoints_template):
    draw_params = dict(
        matchColor=(0,0,255),
        singlePointColor=None,
        matchesMask=matches_mask,
        flags=2
    )
    
    image_matches = cv2.drawMatches(
        template_image, keypoints_template,
        source_image, keypoints_source,
        good_maches, None,
        **draw_params
    )
    return image_matches

def preprocess_image(gray):
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    return gray

def find_image_center_sift(source_image, template_image, min_matches = 10, ransac_threshold = 0.9, debug=False):
    (keypoints_source, descriptors_source), (keypoints_template, descriptors_template) = get_keypoints_descriptors(source_image, template_image, debug)

    matches = get_flann_match(descriptors_source, descriptors_template)
    good_maches = ratio_test(matches)

    if len(good_maches) < min_matches:
        return False, f"Numero De Matches({len(good_maches)}) entre Image e Template nao foi alto o suficiente, tente localizar uma imagem mais descritiva", None
    
    if debug:
        print(f"Total de Matches: {len(matches)} || Total de Matches Bons: {len(good_maches)}")

    matches_mask , mask, M = get_ransac_result(good_maches, keypoints_source, keypoints_template)

    if not matches_mask:
        return False, f"Homography failed, tente usar uma imagem mais descritiva", None
    
    confidence_percent = (np.sum(mask) / len(good_maches))

    if confidence_percent < ransac_threshold:
        return False, f"Homography failed , tente usar uma imagem mais descritiva(Confiança total: {(confidence_percent*100):.1f}% || inliers: {np.sum(mask)})", None
    
    if debug:
        print(f"Confiança total: {(confidence_percent*100):.1f}% || inliers: {np.sum(mask)}")
    h, w = template_image.shape[:2]
    pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M)

    center = np.mean(dst.reshape(-1, 2), axis=0)



    if debug:
        debug_image = get_draw_image(matches_mask, good_maches, source_image, template_image, keypoints_source, keypoints_template)
    
    return True, None, center

# ------------------------------------ #
# Match Template Magnetude
# ------------------------------------ #
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

def find_image_center_match_template(image_source, template, threshold=0.95):
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


