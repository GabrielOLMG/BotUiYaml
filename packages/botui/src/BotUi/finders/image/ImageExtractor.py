import cv2
import numpy as np

from BotUi.finders.BotTargetResult import BotTargetResult

from concurrent.futures import ThreadPoolExecutor, as_completed

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)

class ImageExtractor:
    def __init__(
            self,
            model_type = "rapid_ocr",
            split_images = True,
            search_area:dict={},
            *,
            save_debug_internal=None
        ):
        self.model_type = model_type
        self.split_images = split_images
        self.target_result = BotTargetResult(found=False, error=False, target_type="TEXT")

        # -- Internal Settings -- #
        self.overlap_prop = 0.2
        self.save_debug_internal=save_debug_internal
        self.log_text = f"[ImageExtractor.run [Text Model: {model_type}]"

        # -- Init Search Area Fields-- #
        self.column_target = search_area.get("column", None)
        self.row_target = search_area.get("row", None)
        self.grid_cols = search_area.get("grid_cols", 3)
        self.grid_rows = search_area.get("grid_rows", 3)


    # -----------------------
    # Main
    # -----------------------
    def run(self, source_image, templeta_image=None):
        try:
            return self._run(source_image=source_image, templeta_image=templeta_image)
        except Exception as err:
            import traceback

            tb = traceback.format_exc()
            self.target_result.error = True
            self.target_result.log_message = f"{str(err)} -> {tb}"
            return self.target_result

    def _run(self, source_image, templeta_image):
        # 0) Init
        image = cv2.imread(source_image)
        if image is None:
            self.target_result.error = True
            self.target_result.log_message = f"{self.log_text} Failed to open image: cv2.imread('{source_image}')"
            return self.target_result

        # 1) 
        # images_parts = self._process_image_parts(image)
        # self.target_result.debug_json = images_parts 

        # 3) Flat parts
        # all_raw_results = []
        # for part_results in images_parts.values():
        #     all_raw_results.extend(part_results)


        # 6) Create Debug image
        self.create_debug(image, all_texts, targets_info)

        return self.target_result

    # -----------------------
    # Secondary functions
    # -----------------------

    def _process_image_parts(self, image):
        """
            # Return: {FULL_IMAGE: [{'box':..., 'center':..., 'score':..., 'text':...}]...}
        """
        image_parts = self._split_image(image) if self.split_images else {"FULL": {"image": image, "offset": (0,0)}}
        results = {}

        self._init_model()
        with ThreadPoolExecutor(max_workers=None) as executor:
            # Mapeamos a tarefa para cada partes
            future_to_part = {
                executor.submit(self._extract_single_image, info["image"], info["offset"], name): name 
                for name, info in image_parts.items()
            }
            
            for future in as_completed(future_to_part):
                part_name = future_to_part[future]
                try:
                    results[part_name] = future.result()
                except Exception as exc:
                    print(f"Parte {part_name} gerou uma exceção: {exc}")
                    results[part_name] = []


        return results

    def _extract_single_image(self, image, offset, part_name):
        """
            # Return: [{'box':..., 'center':..., 'score':..., 'text':...}, ...] 
        """

        # 1) 
        model_result = self._run_model(image)
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
            item["R_C"] = part_name

        return model_result
    


    
    # -----------------------
    # Models functions
    # -----------------------
    def _init_model(self):
        self.model = None
        if self.model_type == "rapid_ocr":
            from BotUi.finders.image.models.match_template import MatchTemplateService
            self.model = MatchTemplateService()
            return self.model
        else:
            raise ValueError(f"Non-existent image model: {self.model_type}")
        
    def _run_model(self, source, template):
        if self.model_type == "rapid_ocr":
            from BotUi.finders.image.models.match_template import MatchTemplateService
            return self.model.run(source, template)
        else:
            raise ValueError(f"Non-existent image model: {self.model_type}")

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
        rows = self.grid_rows
        cols = self.grid_cols

        h_step = h // rows
        w_step = w // cols

        ov_h = max(20, int(h_step * self.overlap_prop))
        ov_w = max(20, int(w_step * self.overlap_prop))

        parts = {}
        row_range = [self.row_target] if self.row_target is not None else range(rows)
        col_range = [self.column_target] if self.column_target is not None else range(cols)
        
        for r in row_range:
            for c in col_range:
                y_start = r * h_step
                y_end = (r + 1) * h_step if r < rows - 1 else h
                x_start = c * w_step
                x_end = (c + 1) * w_step if c < cols - 1 else w

                y_start_ov = max(0, y_start - ov_h)
                y_end_ov = min(h, y_end + ov_h)
                x_start_ov = max(0, x_start - ov_w)
                x_end_ov = min(w, x_end + ov_w)

                parts[f"R{r}_C{c}"] = {
                    "image": image[y_start_ov:y_end_ov, x_start_ov:x_end_ov],
                    "offset": (x_start_ov, y_start_ov)
                }

        return parts
        

    # -----------------------
    # Debug functions
    # -----------------------

    def create_debug(self, image, all_texts, texts_filtered):
        image_debug = image.copy()
 
        image_debug = self._draw_grid(image_debug)

        return image_debug

    def _draw_grid(self, image, thickness=1):
        h, w = image.shape[:2]
        rows = self.grid_rows
        cols = self.grid_cols

        h_step = h // rows
        w_step = w // cols

        ov_h = max(20, int(h_step * self.overlap_prop))
        ov_w = max(20, int(w_step * self.overlap_prop))

        for i in range(1, rows):
            y = int(i * h_step)
            cv2.line(image, (0, y), (w, y), RED, thickness)
        for j in range(1, cols):
            x = int(j * w_step)
            cv2.line(image, (x, 0), (x, h), RED, thickness)

        for r in range(rows):
            for c in range(cols):
                y_start = r * h_step
                x_start = c * w_step
                
                y_end = (r + 1) * h_step if r < rows - 1 else h
                x_end = (c + 1) * w_step if c < cols - 1 else w

                y_start_ov = max(0, y_start - ov_h)
                y_end_ov = min(h, y_end + ov_h)
                x_start_ov = max(0, x_start - ov_w)
                x_end_ov = min(w, x_end + ov_w)

                cv2.rectangle(
                    image, 
                    (x_start_ov, y_start_ov), 
                    (x_end_ov, y_end_ov), 
                    BLUE, 
                    1
                )
                
                label = f"R{r}_C{c}"
                cv2.putText(
                    image, label, (x_start + 10, y_start + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED, 1, cv2.LINE_AA
                )

        return image


