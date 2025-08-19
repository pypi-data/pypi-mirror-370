
from typing import Dict, List
import paddle.inference as paddle_infer
import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from .super_resolution import SuperResolution
import tempfile


class LicensePlateRecogniser:


    def __init__(self, model_dir:str, super_res:SuperResolution, use_gpu:bool=False, cpu_threads:int = 20):
        if not os.path.exists(model_dir):
            raise ValueError('that model directory does not exist')
        
        if not isinstance(super_res, SuperResolution):
            raise ValueError('super_res must be an instance of SuperResolution')

        if model_dir[-1] != '/':
            model_dir = model_dir + '/'

        pdmodel     = f"{model_dir}model.pdmodel"
        pdiparams   = f"{model_dir}model.pdiparams"

        if not os.path.isfile(pdmodel):
            raise ValueError('Could not find model.pdmodel')
        
        if not os.path.isfile(pdiparams):
            raise ValueError('Could not find pdiparams')
        
        conf = paddle_infer.Config(pdmodel, pdiparams)

        if use_gpu == False:
            conf.disable_gpu()
            conf.set_cpu_math_library_num_threads(cpu_threads)

        self.__predictor = paddle_infer.create_predictor(conf)
        self.__input_size = (608, 608)
        self.__super_res = super_res
        

    def run_detect_license_plates(self, image_path:str, score_threshold:float=0.3):
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        orig_h, orig_w = img.shape[:2]
        img_resized = cv2.resize(img, self.__input_size)
        img_float = img_resized.astype(np.float32) / 255.0

        mean = np.array([0.485, 0.456, 0.406]).reshape((1, 1, 3))
        std = np.array([0.229, 0.224, 0.225]).reshape((1, 1, 3))
        img_normalized = (img_float - mean) / std

        img_transposed = img_normalized.transpose((2, 0, 1))  # CHW
        input_data = img_transposed[np.newaxis, :, :, :].astype('float32')  # NCHW

        # Prepare im_shape and scale_factor
        im_shape = np.array([[orig_h, orig_w]]).astype('float32')
        scale_factor = np.array([[1.0, 1.0]]).astype('float32')

        # Feed inputs
        input_names = self.__predictor.get_input_names()
        input_handles = {name: self.__predictor.get_input_handle(name) for name in input_names}

        input_handles['image'].reshape(input_data.shape)
        input_handles['image'].copy_from_cpu(input_data)

        input_handles['im_shape'].reshape(im_shape.shape)
        input_handles['im_shape'].copy_from_cpu(im_shape)

        input_handles['scale_factor'].reshape(scale_factor.shape)
        input_handles['scale_factor'].copy_from_cpu(scale_factor)

        # Run inference
        self.__predictor.run()

        # Get outputs
        output_name = self.__predictor.get_output_names()[0]
        output = self.__predictor.get_output_handle(output_name).copy_to_cpu()

        # Postprocess
        detections = []
        for det in output:
            class_id, score, xmin, ymin, xmax, ymax = det
            if score >= score_threshold:
                detections.append({
                    "class_id": int(class_id),
                    "score": float(score),
                    "bbox": [float(xmin), float(ymin), float(xmax), float(ymax)]
                })

        return detections

    def extract_bboxes_from_path(self, image_path: str, detections: list) -> List[Image.Image]:
        image = Image.open(image_path)
        cropped_images = []
        
        for det in detections:
            bbox = det['bbox']
            # Ensure coordinates are within image bounds
            left = max(0, int(bbox[0]))
            top = max(0, int(bbox[1]))
            right = min(image.width, int(bbox[2]))
            bottom = min(image.height, int(bbox[3]))
            cropped = image.crop((left, top, right, bottom))
            cropped_images.append(cropped)

        return cropped_images
    
    def read_text_from_image(self, image:Image.Image, super_resolution:bool=False) -> str:
        
        if super_resolution:
            image = self.__super_res.run_super_resolution(image)

        return pytesseract.image_to_string(
            image,
            config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        ).strip().upper()
    
    def draw_detections(self, image_path, detections, box_color=(255, 0, 0), box_width=3):
        from PIL import Image, ImageDraw, ImageFont

        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        # Load font (fallback if system font not available)
        try:
            font = ImageFont.truetype("arial.ttf", size=18)
        except:
            font = ImageFont.load_default()

        for det in detections:
            bbox = det["bbox"]
            score = det.get("score", None)
            label = det.get("class_id", "")
            x1, y1, x2, y2 = map(int, bbox)

            # Draw rectangle
            draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)

            # Draw score text
            text = f"{label}: {score:.2f}" if score is not None else str(label)

            # ✅ FIX: use font.getbbox for size instead of draw.textsize
            bbox_text = font.getbbox(text)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]

            # Draw background rectangle for text
            draw.rectangle([x1, y1 - text_height, x1 + text_width, y1], fill=box_color)

            # Draw text
            draw.text((x1, y1 - text_height), text, fill=(255, 255, 255), font=font)

        return image


def crop_bboxes_from_detections(
    image_path: str,
    detections: List[Dict],
    score_threshold: float = 0.0
) -> List[Image.Image]:
    """
sr = SuperResolution('.../swinirsr.pth')
lpr = LicensePlateRecogniser('.../models', sr)
plates = crop_bboxes_from_detections(img_path, lpr.run_detect_license_plates(img_path, 0.3), 0.8)

for plate in plates:
    
    """
    image = Image.open(image_path).convert("RGB")
    W, H = image.width, image.height
    crops: List[Image.Image] = []

    for det in detections or []:
        try:
            score = float(det.get("score", 0.0))
            if score < score_threshold:
                continue

            x1, y1, x2, y2 = [float(v) for v in det["bbox"]]
        except Exception:
            # skip malformed detections
            continue

        # Normalize coordinates to a valid, ordered box within image bounds
        left   = max(0.0, min(x1, x2))
        top    = max(0.0, min(y1, y2))
        right  = min(float(W), max(x1, x2))
        bottom = min(float(H), max(y1, y2))

        # Guard against empty/degenerate boxes
        if right - left < 1 or bottom - top < 1:
            continue

        # PIL crop expects (left, upper, right, lower), right/lower are exclusive
        box = (int(round(left)), int(round(top)), int(round(right)), int(round(bottom)))
        crops.append(image.crop(box))

    return crops

def image_to_temp_jpeg(img: Image.Image) -> str:
    # Preserve/normalize mode (handle alpha)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.split()[-1])
        out_img = background
    else:
        out_img = img.convert("RGB")

    # Collect save params
    save_params = {
        "format": "JPEG",
        "quality": 95,          # good quality default
        "optimize": True,
        "subsampling": 0,       # keep best chroma quality
    }

    dpi = img.info.get("dpi")
    if dpi:
        if isinstance(dpi, (int, float)):
            save_params["dpi"] = (dpi, dpi)
        elif isinstance(dpi, tuple) and len(dpi) == 2:
            save_params["dpi"] = dpi

    if "icc_profile" in img.info:
        save_params["icc_profile"] = img.info["icc_profile"]
    if "exif" in img.info:
        save_params["exif"] = img.info["exif"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        out_img.save(tmp, **save_params)
        return tmp.name
    