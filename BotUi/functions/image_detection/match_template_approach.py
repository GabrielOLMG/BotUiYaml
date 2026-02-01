import cv2
import numpy as np

# ------------------------------------ #
# HELPERS
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
    return (float(center_x), float(center_y))

# ------------------------------------ #
# MAIN
# ------------------------------------ #

def find_image_center_match_template(image_source, template, threshold=0.95):
    try:
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
        return False, None, None
    except Exception as err:
        return False, err, None

