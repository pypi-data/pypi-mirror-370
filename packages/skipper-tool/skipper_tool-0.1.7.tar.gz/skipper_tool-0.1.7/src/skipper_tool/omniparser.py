#!/usr/bin/env python3
"""
OmniParser class for UI element detection and annotation.

This class provides a simple interface for:
1. Predicting UI elements (icons) in images using YOLO
2. Annotating images with bounding boxes and labels

Based on the OmniParser v2.0 framework from Microsoft.
Note: OCR functionality has been removed.
"""

from __future__ import annotations

import base64
import io
import logging
import time
from typing import Optional

import numpy as np
import supervision as sv
import torch
from PIL import Image
from torchvision.ops import box_convert

from skipper_tool.annotate import (
    BoxAnnotator,
    MarkHelper,
    annotate,
    plot_boxes_with_marks,
)

# Import from helper modules
from skipper_tool.boxes import (
    get_parsed_content_icon,
    int_box_area,
    remove_overlap_new,
)
from skipper_tool.profiling import profile


# Utility functions from utils.py (non-OCR related)
def get_yolo_model(model_path):
    from ultralytics import YOLO

    model = YOLO(model_path)
    return model


def get_caption_model_processor(
    model_name, model_name_or_path="Salesforce/blip2-opt-2.7b", device=None
):
    if not device:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if model_name == "blip2":
        from transformers import Blip2ForConditionalGeneration, Blip2Processor

        processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        if device == "cpu":
            model = Blip2ForConditionalGeneration.from_pretrained(
                model_name_or_path, device_map=None, torch_dtype=torch.float32
            )
        else:
            model = Blip2ForConditionalGeneration.from_pretrained(
                model_name_or_path, device_map=None, torch_dtype=torch.float16
            ).to(device)
    elif model_name == "florence2":
        from transformers import AutoModelForCausalLM, AutoProcessor

        processor = AutoProcessor.from_pretrained(
            "microsoft/Florence-2-base", trust_remote_code=True
        )
        if device == "cpu":
            model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path, torch_dtype=torch.float32, trust_remote_code=True
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path, torch_dtype=torch.float16, trust_remote_code=True
            ).to(device)
    return {"model": model.to(device), "processor": processor}


def predict_yolo(model, image, box_threshold, imgsz, scale_img, iou_threshold=0.7):
    """Use YOLO model for prediction."""
    start_time = time.time()

    with profile(
        "YOLO prediction",
        "yolo",
        image_size=image.size
        if hasattr(image, "size")
        else str(image.shape if hasattr(image, "shape") else "unknown"),
        box_threshold=box_threshold,
        iou_threshold=iou_threshold,
        imgsz=imgsz,
        scale_img=scale_img,
    ):
        if scale_img:
            result = model.predict(
                source=image,
                conf=box_threshold,
                imgsz=imgsz,
                iou=iou_threshold,
            )
        else:
            result = model.predict(
                source=image,
                conf=box_threshold,
                iou=iou_threshold,
            )

    boxes = result[0].boxes.xyxy
    conf = result[0].boxes.conf
    phrases = [str(i) for i in range(len(boxes))]

    # Log inference results
    runtime = time.time() - start_time
    from skipper_tool.inference_logger import log_yolo_call

    # Prepare image info
    image_info = {
        "size": image.size
        if hasattr(image, "size")
        else str(image.shape if hasattr(image, "shape") else "unknown"),
        "format": "PIL_Image" if hasattr(image, "size") else "numpy_array",
    }

    # Prepare predictions output
    predictions = {
        "boxes": boxes.tolist() if hasattr(boxes, "tolist") else boxes,
        "confidence": conf.tolist() if hasattr(conf, "tolist") else conf,
        "phrases": phrases,
        "num_detections": len(boxes),
    }

    # Log the inference
    log_yolo_call(
        model_name=getattr(model, "model_name", "yolo_model"),
        operation="YOLO prediction",
        image_info=image_info,
        predictions=predictions,
        runtime_seconds=runtime,
        box_threshold=box_threshold,
        iou_threshold=iou_threshold,
        imgsz=imgsz,
        scale_img=scale_img,
    )

    return boxes, conf, phrases


def get_som_labeled_img(
    image_source: str | Image.Image,
    model=None,
    BOX_THRESHOLD=0.05,
    output_coord_in_ratio=False,
    ocr_bbox=None,
    text_scale=0.4,
    text_padding=5,
    draw_bbox_config=None,
    caption_model_processor=None,
    ocr_text=[],
    use_local_semantics=False,
    iou_threshold=0.9,
    prompt=None,
    scale_img=False,
    imgsz=None,
    batch_size=64,
):
    """Process image and get labeled SOM output (without OCR)."""
    if isinstance(image_source, str):
        image_source = Image.open(image_source).convert("RGB")

    w, h = image_source.size
    if not imgsz:
        imgsz = (h, w)

    xyxy, logits, phrases = predict_yolo(
        model=model,
        image=image_source,
        box_threshold=BOX_THRESHOLD,
        imgsz=imgsz,
        scale_img=scale_img,
        iou_threshold=0.1,
    )
    xyxy = xyxy / torch.Tensor([w, h, w, h]).to(xyxy.device)
    image_source = np.asarray(image_source)
    phrases = [str(i) for i in range(len(phrases))]

    # Skip OCR processing and just process YOLO detections
    ocr_bbox_elem = []  # No OCR boxes
    xyxy_elem = [
        {"type": "icon", "bbox": box, "interactivity": True, "content": None}
        for box in xyxy.tolist()
        if int_box_area(box, w, h) > 0
    ]
    filtered_boxes = remove_overlap_new(
        boxes=xyxy_elem, iou_threshold=iou_threshold, ocr_bbox=ocr_bbox_elem
    )

    # sort the filtered_boxes so that the one with 'content': None is at the end
    filtered_boxes_elem = sorted(filtered_boxes, key=lambda x: x["content"] is None)
    # get the index of the first 'content': None
    starting_idx = next(
        (i for i, box in enumerate(filtered_boxes_elem) if box["content"] is None), -1
    )
    filtered_boxes = torch.tensor([box["bbox"] for box in filtered_boxes_elem])
    logging.debug("len(filtered_boxes):", len(filtered_boxes), starting_idx)

    # get parsed icon local semantics
    time1 = time.time()
    if use_local_semantics and caption_model_processor:
        parsed_content_icon = get_parsed_content_icon(
            filtered_boxes,
            starting_idx,
            image_source,
            caption_model_processor,
            prompt=prompt,
            batch_size=batch_size,
        )
        parsed_content_icon_ls = []
        # fill the filtered_boxes_elem None content with parsed_content_icon in order
        for i, box in enumerate(filtered_boxes_elem):
            if box["content"] is None:
                box["content"] = parsed_content_icon.pop(0)
        for i, txt in enumerate(parsed_content_icon):
            parsed_content_icon_ls.append(f"Icon Box ID {str(i)}: {txt}")
    logging.debug("time to get parsed content:", time.time() - time1)

    filtered_boxes = box_convert(boxes=filtered_boxes, in_fmt="xyxy", out_fmt="cxcywh")

    phrases = [i for i in range(len(filtered_boxes))]

    # draw boxes
    if draw_bbox_config:
        annotated_frame, label_coordinates = annotate(
            image_source=image_source,
            boxes=filtered_boxes,
            logits=logits,
            phrases=phrases,
            **draw_bbox_config,
        )
    else:
        annotated_frame, label_coordinates = annotate(
            image_source=image_source,
            boxes=filtered_boxes,
            logits=logits,
            phrases=phrases,
            text_scale=text_scale,
            text_padding=text_padding,
        )

    pil_img = Image.fromarray(annotated_frame)
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode("ascii")
    if output_coord_in_ratio:
        label_coordinates = {
            k: [v[0] / w, v[1] / h, v[2] / w, v[3] / h]
            for k, v in label_coordinates.items()
        }
        assert w == annotated_frame.shape[1] and h == annotated_frame.shape[0]

    return encoded_image, label_coordinates, filtered_boxes_elem


class OmniParser:
    """
    OmniParser class for UI element detection and annotation.

    This class combines YOLO object detection, OCR, and optional caption models
    to detect and annotate UI elements in images.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the OmniParser with model configurations.

        Args:
            config: Dictionary containing model paths and configurations.
                   If None, uses default configuration.
        """
        # Default configuration
        default_config = {
            "som_model_path": "/Users/nharada/Models/omniparser/model.pt",
            "caption_model_name": None,  # Set to 'blip2' or 'florence2' to enable
            "caption_model_path": None,
            "box_threshold": 0.05,
            "iou_threshold": 0.1,
            "use_paddleocr": True,
            "imgsz": 640,
            "use_local_semantics": False,
            "batch_size": 64,
        }

        self.config = {**default_config, **(config or {})}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initialize models
        self._load_models()

        # Initialize helpers
        self.som_generator = MarkHelper()

        logging.debug(f"OmniParser initialized on {self.device}!")

    def _load_models(self):
        """Load the required models."""
        # Load YOLO model for icon detection
        self.yolo_model = get_yolo_model(model_path=self.config["som_model_path"])

        # Load caption model if specified
        if self.config["caption_model_name"] and self.config["caption_model_path"]:
            self.caption_model_processor = get_caption_model_processor(
                model_name=self.config["caption_model_name"],
                model_name_or_path=self.config["caption_model_path"],
                device=self.device,
            )
        else:
            self.caption_model_processor = None

    def predict(
        self,
        image: str | Image.Image | np.ndarray,
        return_annotated_image: bool = True,
        **annotation_kwargs,
    ) -> dict:
        """
        Predict UI elements in the image and optionally return annotated image.

        Args:
            image: Input image as file path, PIL Image, or numpy array
            return_annotated_image: Whether to include annotated image in results
            **annotation_kwargs: Additional arguments for annotation (thickness, text_scale, etc.)

        Returns:
            Dictionary containing:
            - 'boxes': List of bounding boxes in format [x1, y1, x2, y2]
            - 'labels': List of element labels/descriptions
            - 'coordinates': Dictionary mapping element IDs to coordinates
            - 'parsed_content': List of parsed content descriptions
            - 'image_size': Tuple of (width, height)
            - 'annotated_image': PIL Image with annotations (if return_annotated_image=True)
        """
        # Convert input to PIL Image
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        elif not isinstance(image, Image.Image):
            raise ValueError("Input must be a file path, PIL Image, or numpy array")

        # Configure drawing parameters
        box_overlay_ratio = image.size[0] / 3200
        draw_bbox_config = {
            "text_scale": 0.8 * box_overlay_ratio,
            "text_thickness": max(int(2 * box_overlay_ratio), 1),
            "text_padding": max(int(3 * box_overlay_ratio), 1),
            "thickness": max(int(3 * box_overlay_ratio), 1),
        }

        # Get UI element predictions (no OCR)
        _, label_coordinates, parsed_content_list = get_som_labeled_img(
            image,
            self.yolo_model,
            BOX_THRESHOLD=self.config["box_threshold"],
            output_coord_in_ratio=False,
            ocr_bbox=None,
            draw_bbox_config=draw_bbox_config,
            caption_model_processor=self.caption_model_processor,
            ocr_text=[],
            iou_threshold=self.config["iou_threshold"],
            imgsz=self.config["imgsz"],
            use_local_semantics=self.config["use_local_semantics"],
            batch_size=self.config["batch_size"],
        )

        # Extract boxes and labels
        boxes = []
        labels = []
        for key, coords in label_coordinates.items():
            # coords are in xywh format, convert to xyxy
            x, y, w, h = coords
            boxes.append([x, y, x + w, y + h])
            labels.append(f"Element {key}")

        # Format parsed content
        parsed_content = []
        for i, content in enumerate(parsed_content_list):
            if hasattr(content, "get"):  # Dictionary-like object
                parsed_content.append(content.get("content", f"Element {i}"))
            else:
                parsed_content.append(str(content))

        result = {
            "boxes": boxes,
            "labels": labels,
            "coordinates": label_coordinates,
            "parsed_content": parsed_content,
            "image_size": image.size,
        }

        # Add annotated image if requested
        if return_annotated_image:
            annotated_image = self.annotate(image, result, **annotation_kwargs)
            result["annotated_image"] = annotated_image

        return result

    def annotate(
        self,
        image: str | Image.Image | np.ndarray,
        predictions: Optional[dict] = None,
        box_color: tuple[int, int, int] = (255, 0, 0),
        text_color: tuple[int, int, int] = (255, 255, 255),
        thickness: int = 3,
        text_scale: float = 0.8,
    ) -> Image.Image:
        """
        Internal method for annotating images. Use predict() with return_annotated_image=True instead.
        """
        # Convert input to PIL Image
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        elif not isinstance(image, Image.Image):
            raise ValueError("Input must be a file path, PIL Image, or numpy array")

        # Get predictions if not provided
        if predictions is None:
            predictions = self.predict(image, return_annotated_image=False)

        # Convert PIL to numpy for annotation
        image_np = np.array(image)

        # Create detections for supervision
        if predictions["boxes"]:
            boxes_array = np.array(predictions["boxes"])
            detections = sv.Detections(xyxy=boxes_array)

            # Create labels with element IDs
            labels = [f"{i}" for i in range(len(predictions["boxes"]))]

            # Use BoxAnnotator for consistent styling
            box_annotator = BoxAnnotator(
                thickness=thickness,
                text_scale=text_scale,
                text_padding=5,
                text_thickness=2,
            )

            # Annotate the image
            annotated_frame = box_annotator.annotate(
                scene=image_np.copy(),
                detections=detections,
                labels=labels,
                image_size=image.size,
            )

            return Image.fromarray(annotated_frame)
        else:
            # No detections found, return original image
            return image

    def annotate_with_som(
        self,
        image: str | Image.Image | np.ndarray,
        predictions: Optional[dict] = None,
        add_marks: bool = True,
    ) -> Image.Image:
        """
        Internal method for SOM-style annotation. Use predict() with return_annotated_image=True instead.
        """
        # Convert input to PIL Image
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        elif not isinstance(image, Image.Image):
            raise ValueError("Input must be a file path, PIL Image, or numpy array")

        # Get predictions if not provided
        if predictions is None:
            predictions = self.predict(image, return_annotated_image=False)

        if not predictions["boxes"]:
            return image

        # Convert boxes to yxhw format for SOM plotting
        bboxes_yxhw = []
        w, h = image.size

        for box in predictions["boxes"]:
            x1, y1, x2, y2 = box
            # Convert to normalized yxhw format
            y_norm = y1 / h
            x_norm = x1 / w
            h_norm = (y2 - y1) / h
            w_norm = (x2 - x1) / w
            bboxes_yxhw.append([y_norm, x_norm, h_norm, w_norm])

        # Use SOM plotting function
        annotated_image = plot_boxes_with_marks(
            image.copy(),
            bboxes_yxhw,
            self.som_generator,
            linewidth=3,
            edgecolor=(255, 0, 0),
            normalized_to_pixel=True,
            add_mark=add_marks,
        )

        return annotated_image

    def get_element_at_point(self, predictions: dict, x: int, y: int) -> Optional[dict]:
        """
        Get the UI element at a specific point in the image.

        Args:
            predictions: Predictions from predict() method
            x, y: Pixel coordinates

        Returns:
            Dictionary with element information if found, None otherwise
        """
        for i, box in enumerate(predictions["boxes"]):
            x1, y1, x2, y2 = box
            if x1 <= x <= x2 and y1 <= y <= y2:
                return {
                    "index": i,
                    "box": box,
                    "label": predictions["labels"][i],
                    "content": predictions["parsed_content"][i]
                    if i < len(predictions["parsed_content"])
                    else None,
                }
        return None

    def save_annotated_image(self, image: Image.Image, filename: str):
        """
        Save annotated image to file.

        Args:
            image: PIL Image to save
            filename: Output filename
        """
        image.save(filename)
        logging.debug(f"Annotated image saved to: {filename}")
