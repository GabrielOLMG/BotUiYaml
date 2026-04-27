import cv2
import numpy as np

from BotUi.finders.BotTargetResult import BotTargetResult
from BotUi.finders.text.models.rapid_ocr import RapidOCRService

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)

class TextExtractor:
    def __init__(
            self,
            model_type = "rapid_ocr",
            split_images = True,
            columns_split = 3,
            rows_split = 3,
            in_text = True,
            position = 0,
            save_debug_internal=False
        ):
        self.model_type = model_type
        self.split_images = split_images
        self.target_result = BotTargetResult(found=False, error=False, target_type="TEXT")

        # -- Internal Settings -- #
        self.save_debug_internal=save_debug_internal
        self.log_text = f"[TextExtractor.run [Text Model: {model_type}]"

        # -- External Settings -- #
        self.in_text = in_text
        self.columns_split = columns_split
        self.rows_split = rows_split
        self.position = position


    # -----------------------
    # Main
    # -----------------------
    def run(self, image_path, text_target=None):
        try:
            return self._run(image_path, text_target=text_target)
        except Exception as err:
            import traceback

            tb = traceback.format_exc()
            self.target_result.error = True
            self.target_result.log_message = f"{str(err)} -> {tb}"
            raise self.target_result

    def _run(self, image_path, text_target):
        image = cv2.imread(image_path)
        if image is None:
            self.target_result.error = True
            self.target_result.log_message = f"{self.log_text} Failed to open image: cv2.imread('{image_path}')"
            return self.target_result
 

        images_parts = self._process_image_parts(image)
        self.target_result.debug_json = images_parts

        if not text_target: # Crair uma image de debug aqui?
            self.target_result.text_target = f"No text to detect"
            return self.target_result


        parts_checked = {}
        for part_name, results in images_parts.items(): 
            checked = []
            for result in results:
                text_result = result["text"]
                if (self.in_text and text_target in text_result) or (not self.in_text and text_target == text_result):
                    checked.append(result)
            parts_checked[part_name] = checked
        
        merged = self._merge_all_parts_results(parts_checked)
        merged_sorted = sorted(
            merged,
            key=lambda c: (
                c["center"][1],            # top → bottom
                c["center"][0],            # left → right
                -c.get("score", 0)         # segurança (evita crash)
            )
        )

        # TODO: Poder mais de um tipo de debug?
        image_debug = self.debug(image, merged_sorted)
        self.target_result.debug_image = image_debug
        
        total_found = len(merged_sorted)
        if total_found == 0:
            self.target_result.log_message = f"{self.log_text} Object Not Found"
        elif self.position > total_found:
            self.target_result.error = True # Talvez remover para a pesosa poder alterar no debug?
            self.target_result.log_message = f"{self.log_text} A total of {total_found} texts were found, but the desired position was {self.position}. (OBS: The position starts at 0)"
            return self.target_result
        else:
            target_info = merged_sorted[self.position]
            self.target_result.center = target_info["center"]
            self.target_result.found = True

        return self.target_result


    # -----------------------
    # Secondary functions
    # -----------------------

    def _process_image_parts(self, image):
        """
            # Return: {FULL_IMAGE: [{'box':..., 'center':..., 'score':..., 'text':...}]...}
        """
        image_parts = {}
        if self.split_images:
            image_parts = self._split_image(image)
        image_parts["FULL_IMAGE"] = {
            "image": image,
            "offset": (0,0)
        } 

        results = {}
        for part_name, part_info in image_parts.items():
            image = part_info["image"]
            offset = part_info["offset"]
            image_part_result = self._extract_single_image(image, offset)
            results[part_name] = image_part_result
        
        return results

    def _extract_single_image(self, image, offset):
        """
            # Return: [{'box':..., 'center':..., 'score':..., 'text':...}, ...] 
        """
        # 1) 
        model_result = self._get_model_run(image)
        if not model_result:
            return []
        
        # 1.5)
        self._check_model_result(model_result)

        # 2)
        model_result = self._compute_centers(model_result)

        # 3) 
        x_off, y_off = offset

        for item in model_result:
            box = item["box"]

            item["box"] = [
                [x + x_off, y + y_off]
                for x, y in box
            ]

            cx, cy = item["center"]
            item["center"] = [cx + x_off, cy + y_off]

        return model_result
    
    # -----------------------
    # Helpers functions
    # -----------------------

    def _compute_centers(self, results):
        results_with_centers = []

        for result in results:
            box = result["box"]
            pts = np.array(box, dtype=np.int32)

            x_min, y_min = pts[:, 0].min(), pts[:, 1].min()
            x_max, y_max = pts[:, 0].max(), pts[:, 1].max()

            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2

            results_with_centers.append({
                "box": result["box"],
                "text": result["text"],
                "score": result["score"],
                "center": [center_x, center_y]
            })

        return results_with_centers
    
    def _get_model_run(self, image):
        if self.model_type == "rapid_ocr":
            return RapidOCRService().run(image)
        else:
            raise ValueError(f"Non-existent text model: {self.model_type}")
    
    def _check_model_result(self, results):
        if not isinstance(results, list):
            raise TypeError(f"Expected list, got {type(results)}")

        for i, item in enumerate(results):
            if not isinstance(item, dict):
                raise TypeError(f"Item {i} is not a dict: {item}")

            required_keys = {"box", "text", "score"}
            if not required_keys.issubset(item.keys()):
                raise ValueError(f"Item {i} missing keys: {item}")

            if not isinstance(item["text"], str):
                raise TypeError(f"Item {i} has invalid text: {item}")

            if not isinstance(item["score"], (int, float)):
                raise TypeError(f"Item {i} has invalid score: {item}")
    
    def _split_image(self, image):
        h, w = image.shape[:2]
        rows = self.rows_split
        cols = self.columns_split

        h_step = h // rows
        w_step = w // cols

        parts = {}

        for r in range(rows):
            for c in range(cols):
                y_start = r * h_step
                y_end = (r + 1) * h_step if r < rows - 1 else h

                x_start = c * w_step
                x_end = (c + 1) * w_step if c < cols - 1 else w

                parts[f"R{r}_C{c}"] = {
                    "image": image[y_start:y_end, x_start:x_end],
                    "offset": (x_start, y_start)
                }

        return parts
    
    def _merge_all_parts_results(self, result):
        all_results = []

        for part_results in result.values():
            all_results.extend(part_results)

        return self._deduplicate_results(all_results)

    def _deduplicate_results(self, results):
        merged = []

        for r in results:
            found = False

            for i, m in enumerate(merged):
                if self._same_detection(r, m):
                    if r["score"] > m["score"]:
                        merged[i] = r
                    found = True
                    break

            if not found:
                merged.append(r)

        return merged

    def _same_detection(self, a, b, dist=10): # TODO: Substituir por IOU da bbox!
        return (
            a["text"] == b["text"] and
            abs(a["center"][0] - b["center"][0]) < dist and
            abs(a["center"][1] - b["center"][1]) < dist
        )
    
    # -----------------------
    # Debug functions
    # -----------------------

    def debug(self, image, texts_info):
        image_cp = image.copy()

        image_debug = self._draw_grid(image_cp)

        image_debug = self._get_bbox_texts(image_debug, texts_info)



        if self.save_debug_internal:
            cv2.imwrite("/app/data/bbox_texts_debug.png", image_debug)

        return image_debug


    def _draw_grid(self, image, thickness=2):
        h, w = image.shape[:2]
        rows = self.rows_split
        cols = self.columns_split

        row_height = h / rows
        col_width = w / cols

        for i in range(1, rows):
            y = int(i * row_height)
            cv2.line(image, (0, y), (w, y), RED, thickness)

        for j in range(1, cols):
            x = int(j * col_width)
            cv2.line(image, (x, 0), (x, h), RED, thickness)

        for i in range(rows):
            for j in range(cols):
                x = int(j * col_width + 10) 
                y = int(i * row_height + 30)

                label = f"R{i}_C{j}"

                cv2.putText(
                    image,
                    label,
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    RED,
                    2,
                    cv2.LINE_AA
                )

        return image


    def _get_bbox_texts(self, image, texts_info):
        for index, text_info in enumerate(texts_info):
            box = np.array(text_info["box"], dtype=np.int32)
            cx, cy = map(int, text_info["center"])

            if index == self.position:
                cv2.polylines(image, [box], True, GREEN, 2)
            else:
                cv2.polylines(image, [box], True, BLUE, 2)
            cv2.putText(
                image,
                f"[{index}] {text_info['score']*100:.2f}%",
                (cx, cy - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                RED,
                2
            )
        
        return image


