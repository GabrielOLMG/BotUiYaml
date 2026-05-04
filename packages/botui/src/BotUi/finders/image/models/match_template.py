import cv2

class MatchTemplateService:
    def __init__(self, threshold=0.95):
        self.threshold = threshold

    def run(self, source, template):
        # 0)
        source_magnitude = self._get_magnitude(source)
        template_magnitude = self._get_magnitude(template)

        # 1)
        correlated_matrix_norm = cv2.matchTemplate(
            source_magnitude.astype(np.float32),
            template_magnitude.astype(np.float32),
            cv2.TM_CCORR_NORMED
        )

        # 2)
        indices = np.where(correlated_matrix_norm >= self.threshold)


        # 3
        h, w = template.shape[:2]
        results = []

        # 4)
        for row, col in zip(*indices):
            score = float(correlated_matrix_norm[row, col])
            
            box = [int(col), int(row), int(col + w), int(row + h)]
            
            results.append({
                "box": box,
                "score": score,
            })

        return results


    def _get_magnitude(self, image):
        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(gx, gy)
        return magnitude

