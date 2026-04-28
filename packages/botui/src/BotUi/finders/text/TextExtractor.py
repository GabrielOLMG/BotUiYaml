import cv2
import numpy as np

from BotUi.finders.BotTargetResult import BotTargetResult



from concurrent.futures import ThreadPoolExecutor, as_completed

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
            save_debug_internal=False,
            column_target = None,
            row_target = None,
        ):
        self.model_type = model_type
        self.split_images = split_images
        self.target_result = BotTargetResult(found=False, error=False, target_type="TEXT")

        # -- Internal Settings -- #
        self.overlap = 100
        self.save_debug_internal=save_debug_internal
        self.log_text = f"[TextExtractor.run [Text Model: {model_type}]"

        # -- External Settings -- #
        self.in_text = in_text
        self.columns_split = columns_split
        self.rows_split = rows_split
        self.position = position
        self.column_target = column_target
        self.row_target = row_target 


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
            return self.target_result

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

        all_raw_results = []
        for part_results in images_parts.values():
            all_raw_results.extend(part_results)

        merged_results = self._deduplicate_results(all_raw_results)


        final_candidates = []
        for res in merged_results:
            text_res = res["text"]
            if (self.in_text and text_target in text_res) or (not self.in_text and text_target == text_res):
                final_candidates.append(res)


        merged_sorted = sorted(
            final_candidates,
            key=lambda c: (c["center"][1], c["center"][0], -c["score"])
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
        image_parts = self._split_image(image) if self.split_images else {"FULL": {"image": image, "offset": (0,0)}} # TODO: Mudar split para ter uma sobreposicaos
        results = {}

        self._init_model()
        with ThreadPoolExecutor(max_workers=None) as executor:
            # Mapeamos a tarefa para cada parte
            future_to_part = {
                executor.submit(self._extract_single_image, info["image"], info["offset"]): name 
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

    def _extract_single_image(self, image, offset):
        """
            # Return: [{'box':..., 'center':..., 'score':..., 'text':...}, ...] 
        """

        h, w = image.shape[:2]
        image = cv2.resize(image, (w*2, h*2), interpolation=cv2.INTER_CUBIC)

        # 1) 
        model_result = self._run_model(image)
        if not model_result:
            return []
        for item in model_result:
            item["box"] = [[x / 2, y / 2] for x, y in item["box"]]
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
    # Models functions
    # -----------------------
    def _init_model(self):
        if self.model_type == "rapid_ocr":
            from BotUi.finders.text.models.rapid_ocr import RapidOCRService
            return RapidOCRService._get_model()
        elif self.model_type == "doc_ocr":
            from BotUi.finders.text.models.doctr import DoctrService
            return DoctrService._get_model()
        # elif self.model_type == "pp_ocrv4":
        #     from BotUi.finders.text.models.pp_ocrv4 import PaddleOCRV4
        #     return PaddleOCRV4._get_model()
        # elif self.model_type == "easy_ocr":
        #     from BotUi.finders.text.models.easy_ocr import EasyOCRService
        #     return EasyOCRService._get_model()
        else:
            raise ValueError(f"Non-existent text model: {self.model_type}")
    
    def _run_model(self, image):
        if self.model_type == "rapid_ocr":
            from BotUi.finders.text.models.rapid_ocr import RapidOCRService
            return RapidOCRService.run(image)
        elif self.model_type == "doc_ocr":
            from BotUi.finders.text.models.doctr import DoctrService
            return DoctrService.run(image)
        # elif self.model_type == "pp_ocrv4":
        #     from BotUi.finders.text.models.pp_ocrv4 import PaddleOCRV4
        #     return PaddleOCRV4.run(image)
        # elif self.model_type == "easy_ocr":
        #     from BotUi.finders.text.models.easy_ocr import EasyOCRService
        #     return EasyOCRService.run(image)
        else:
            raise ValueError(f"Non-existent text model: {self.model_type}")

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
        rows = self.rows_split
        cols = self.columns_split

        h_step = h // rows
        w_step = w // cols

        parts = {}

        for r in range(rows):
            if self.row_target and r != self.row_target:
                continue
            for c in range(cols):
                if self.column_target and r != self.column_target:
                    continue
                y_start = r * h_step
                y_end = (r + 1) * h_step if r < rows - 1 else h
                x_start = c * w_step
                x_end = (c + 1) * w_step if c < cols - 1 else w

                y_start_ov = max(0, y_start - self.overlap)
                y_end_ov = min(h, y_end + self.overlap)
                x_start_ov = max(0, x_start - self.overlap)
                x_end_ov = min(w, x_end + self.overlap)

                parts[f"R{r}_C{c}"] = {
                    "image": image[y_start_ov:y_end_ov, x_start_ov:x_end_ov],
                    "offset": (x_start_ov, y_start_ov)
                }

        return parts
    

    # -----------------------
    # Merge functions
    # -----------------------

    def _merge_all_parts_results(self, result):
        all_results = []

        for part_results in result.values():
            all_results.extend(part_results)

        return self._deduplicate_results(all_results)


    def _calculate_iou(self, boxA, boxB):
        # Transforma listas de pontos [[x,y], ...] em coordenadas x1, y1, x2, y2
        boxA = np.array(boxA)
        boxB = np.array(boxB)
        
        xA = max(boxA[:, 0].min(), boxB[:, 0].min())
        yA = max(boxA[:, 1].min(), boxB[:, 1].min())
        xB = min(boxA[:, 0].max(), boxB[:, 0].max())
        yB = min(boxA[:, 1].max(), boxB[:, 1].max())

        interArea = max(0, xB - xA) * max(0, yB - yA)
        
        boxAArea = (boxA[:, 0].max() - boxA[:, 0].min()) * (boxA[:, 1].max() - boxA[:, 1].min())
        boxBArea = (boxB[:, 0].max() - boxB[:, 0].min()) * (boxB[:, 1].max() - boxB[:, 1].min())
        
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
        return iou

    def _same_detection(self, a, b, iou_threshold=0.4):
        # Se o texto for idêntico e as caixas se sobrepõem muito
        if a["text"] == b["text"]:
            return self._calculate_iou(a["box"], b["box"]) > iou_threshold
        return False

    def _deduplicate_results(self, results):
        if not results: return []
        
        # Ordena por score para garantir que manteremos o de maior confiança
        merged = []

        for r in results:
            is_duplicate = False
            for m in merged:
                if self._same_detection(r, m):
                    is_duplicate = True
                    break
            if not is_duplicate:
                merged.append(r)
        return merged
    
    # -----------------------
    # Debug functions
    # -----------------------

    def debug(self, image, texts_info):
        image_debug = image.copy()

        image_debug = self._draw_grid(image_debug)

        image_debug = self._get_bbox_texts(image_debug, texts_info)



        if self.save_debug_internal:
            cv2.imwrite("/app/data/bbox_texts_debug.png", image_debug)

        return image_debug

    def _draw_grid(self, image, thickness=1):
        h, w = image.shape[:2]
        rows = self.rows_split
        cols = self.columns_split

        h_step = h // rows
        w_step = w // cols

        for i in range(1, rows):
            y = int(i * h_step)
            cv2.line(image, (0, y), (w, y), RED, thickness)
        for j in range(1, cols):
            x = int(j * w_step)
            cv2.line(image, (x, 0), (x, h), RED, thickness)

        for r in range(rows):
            for c in range(cols):
                y_start = r * h_step
                y_end = (r + 1) * h_step if r < rows - 1 else h
                x_start = c * w_step
                x_end = (c + 1) * w_step if c < cols - 1 else w

                y_start_ov = max(0, y_start - self.overlap)
                y_end_ov = min(h, y_end + self.overlap)
                x_start_ov = max(0, x_start - self.overlap)
                x_end_ov = min(w, x_end + self.overlap)

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


