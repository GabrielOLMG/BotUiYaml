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
            in_text = True,
            position = 0,
            search_area:dict={},
            *,
            save_debug_internal=False
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
        self.position = position

        # -- Init Search Area Fields-- #
        self.column_target = search_area.get("row", None)
        self.row_target = search_area.get("column", None)
        self.grid_cols = search_area.get("grid_cols", 3)
        self.grid_rows = search_area.get("grid_rows", 3)


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
        # 0) Init
        image = cv2.imread(image_path)
        if image is None:
            self.target_result.error = True
            self.target_result.log_message = f"{self.log_text} Failed to open image: cv2.imread('{image_path}')"
            return self.target_result
 
        # 1) Detect Text for each image part
        images_parts = self._process_image_parts(image)
        self.target_result.debug_json = images_parts 

        # 3) Flat parts
        all_raw_results = []
        for part_results in images_parts.values():
            all_raw_results.extend(part_results)

        # 4) join possible duplicate texts
        all_texts = self._deduplicate_results(all_raw_results)
        
        # 5) Filter target text
        targets_info = self._filter_result_and_sort(all_texts, text_target)

        # 6) Create Debug image
        self.create_debug(image, all_texts, targets_info)
        self.target_result.debug_json = {"result": all_texts} 

        # 7) Final Filter
        total_found = len(targets_info)
        if not text_target:
            self.target_result.text_target = f"No text to detect"
        elif total_found == 0:
            self.target_result.log_message = f"{self.log_text} Object Not Found"
        elif self.position > total_found:
            self.target_result.error = True # Talvez remover para a pesosa poder alterar no debug?
            self.target_result.log_message = f"{self.log_text} A total of {total_found} texts were found, but the desired position was {self.position}. (OBS: The position starts at 0)"
        else:
            target_info = targets_info[self.position]
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
            item["R_C"] = part_name

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
        rows = self.grid_rows
        cols = self.grid_cols

        h_step = h // rows
        w_step = w // cols

        parts = {}
        row_range = [self.row_target] if self.row_target is not None else range(rows)
        col_range = [self.column_target] if self.column_target is not None else range(cols)
        for r in row_range:
            for c in col_range:
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
    
    def _filter_result_and_sort(self, result, text_target):
        final_candidates = []
        if not text_target:
            final_candidates = result
        else:
            for res in result: #TODO: Deixar melhor!
                text_res = res["text"]
                if (self.in_text and text_target in text_res) or (not self.in_text and text_target == text_res):
                    final_candidates.append(res)
        
        merged_sorted = sorted(
            final_candidates,
            key=lambda c: (c["center"][1], c["center"][0], -c["score"])
        )
        
        return merged_sorted
    
    # -----------------------
    # Merge functions
    # -----------------------
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

    def create_debug(self, image, all_texts, texts_filtered):
        image_debug = image.copy()
 
        image_debug = self._draw_grid(image_debug)

        if len(texts_filtered) < len(all_texts):
            image_debug = self._get_bbox_texts(image_debug, texts_filtered)
        else:
            image_debug = self._get_bbox_texts(image_debug, all_texts, show_part=True)

        if self.save_debug_internal:
            cv2.imwrite("/app/data/bbox_texts_debug.png", image_debug)

        self.target_result.debug_image = image_debug

        return image_debug

    def _draw_grid(self, image, thickness=1):
        h, w = image.shape[:2]
        rows = self.grid_rows
        cols = self.grid_cols

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

    def _get_bbox_texts(self, image, texts_info, show_part=False):
        overlay = image.copy()
        
        for index, text_info in enumerate(texts_info):
            box = np.array(text_info["box"], dtype=np.int32)
            
            # Cores para o desenho
            GREEN = (0, 255, 0)
            BLUE = (255, 0, 0)
            RED = (0, 0, 255)
            WHITE = (255, 255, 255)

            if not show_part:
                # --- COMPORTAMENTO ORIGINAL (MANTER EXATAMENTE COMO ESTAVA) ---
                cx, cy = map(int, text_info["center"])
                color = GREEN if index == self.position else BLUE
                
                cv2.polylines(image, [box], True, color, 2)
                cv2.putText(
                    image,
                    f"[{index}] {text_info['score']*100:.2f}%",
                    (cx, cy - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    RED,
                    2
                )
            else:
                # --- COMPORTAMENTO NOVO (PARA DEBUG DE POSIÇÃO R_C) ---
                tl_x, tl_y = text_info["box"][0] # Canto Superior Esquerdo
                
                # Desenha a BBox e preenche o overlay
                cv2.polylines(image, [box], True, BLUE, 2)
                cv2.fillPoly(overlay, [box], BLUE)
                
                label = f" {text_info['R_C']} "
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 0.4
                thickness = 1
                
                # Calcula tamanho para o fundo vermelho
                (tw, th), _ = cv2.getTextSize(label, font, scale, thickness)
                
                # Retângulo de fundo saindo do Top-Left para cima
                cv2.rectangle(image, (int(tl_x), int(tl_y - th - 5)), (int(tl_x + tw), int(tl_y)), RED, -1)
                
                # Texto branco sobre o fundo vermelho
                cv2.putText(
                    image, 
                    label, 
                    (int(tl_x), int(tl_y - 5)), 
                    font, 
                    scale, 
                    WHITE, 
                    thickness, 
                    lineType=cv2.LINE_AA
                )

        if show_part:
            # Aplica transparência apenas no modo show_part
            image = cv2.addWeighted(overlay, 0.15, image, 0.85, 0)
            
        return image


