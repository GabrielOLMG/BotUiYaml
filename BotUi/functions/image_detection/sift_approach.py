import cv2
import numpy as np

# ------------------------------------ #
# HELPERS
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



# ------------------------------------ #
# MAIN
# ------------------------------------ #

def find_image_center_sift(source_image, template_image, min_matches = 10, ransac_threshold = 0.9, debug=False):
    try: 
        (keypoints_source, descriptors_source), (keypoints_template, descriptors_template) = get_keypoints_descriptors(source_image, template_image, debug)

        matches = get_flann_match(descriptors_source, descriptors_template)
        good_maches = ratio_test(matches)

        if len(good_maches) < min_matches:
            # TODO: TO LOG: f"Numero De Matches({len(good_maches)}) entre Image e Template nao foi alto o suficiente, tente localizar uma imagem mais descritiva"
            return False, None, None
        
        # if debug:
        #     print(f"Total de Matches: {len(matches)} || Total de Matches Bons: {len(good_maches)}")

        matches_mask , mask, M = get_ransac_result(good_maches, keypoints_source, keypoints_template)

        if matches_mask is not None:
            # TODO: To LOG f"Homography failed, tente usar uma imagem mais descritiva"
            return False, None, None
        
        confidence_percent = (np.sum(mask) / len(good_maches))

        if confidence_percent < ransac_threshold:
            # TODO: To LOG f"Homography failed , tente usar uma imagem mais descritiva(Confiança total: {(confidence_percent*100):.1f}% || inliers: {np.sum(mask)})"
            return False, None, None
        
        # if debug:
        #     print(f"Confiança total: {(confidence_percent*100):.1f}% || inliers: {np.sum(mask)}")

        h, w = template_image.shape[:2]
        pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts, M)

        center = np.mean(dst.reshape(-1, 2), axis=0)

        # if debug:
        #     debug_image = get_draw_image(matches_mask, good_maches, source_image, template_image, keypoints_source, keypoints_template)

        return True, None, center.tolist()
        
    except Exception as err:
        return False, err, None
    


