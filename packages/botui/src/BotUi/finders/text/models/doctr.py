import numpy as np
import cv2 
import torch

class DoctrService:
    _predictor = None


    @classmethod
    def _get_model(cls):
        from doctr.models import ocr_predictor

        if cls._predictor is None:
            torch.set_num_threads(4) 
            
            cls._predictor = ocr_predictor(
                det_arch='db_mobilenet_v3_large', 
                reco_arch='crnn_mobilenet_v3_small', 
                pretrained=True,
                assume_straight_pages=True,
                preserve_aspect_ratio=True
            )
            cls._predictor.reco_predictor.model.cfg['input_shape'] = (48, 256)
            fake_img = np.zeros((300, 300, 3), dtype=np.uint8)
            cls._predictor([fake_img])
            
            
        return cls._predictor


    @classmethod
    def run(cls, image):
        """
        Recebe uma imagem (OpenCV/Numpy BGR)
        Retorna: [{'box': ..., 'text': ..., 'score': ...}] agrupado por linhas
        """
        predictor = cls._get_model()
        h, w = image.shape[:2]
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        result = predictor([image_rgb])
        
        output = result.export()
        
        final_results = []
        
        for page in output['pages']:
            for block in page['blocks']:
                for line in block['lines']:
                    words = line['words']
                    if not words:
                        continue

                    # 1. Agrupar texto da linha com espaços reais
                    full_line_text = " ".join([word['value'] for word in words])
                    
                    # 2. Média de confiança da frase
                    avg_confidence = sum([word['confidence'] for word in words]) / len(words)

                    # 3. Calcular Bounding Box que engloba TODA a linha (Min/Max)
                    # Geometria docTR: ((x_min, y_min), (x_max, y_max)) normalizados
                    all_x_min = min([w_obj['geometry'][0][0] for w_obj in words])
                    all_y_min = min([w_obj['geometry'][0][1] for w_obj in words])
                    all_x_max = max([w_obj['geometry'][1][0] for w_obj in words])
                    all_y_max = max([w_obj['geometry'][1][1] for w_obj in words])

                    # 4. Converter normalizado (0-1) -> Pixels reais
                    box = [
                        [int(all_x_min * w), int(all_y_min * h)], # Top-left
                        [int(all_x_max * w), int(all_y_min * h)], # Top-right
                        [int(all_x_max * w), int(all_y_max * h)], # Bottom-right
                        [int(all_x_min * w), int(all_y_max * h)]  # Bottom-left
                    ]
                    
                    final_results.append({
                        "box": box,
                        "text": full_line_text,
                        "score": avg_confidence
                    })
        
        return final_results