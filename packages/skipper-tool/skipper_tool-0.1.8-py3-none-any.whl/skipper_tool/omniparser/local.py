#!/usr/bin/env python3
"""
Local OmniParser implementation using YOLO models.

This module provides:
1. LocalOmniParser class for local YOLO execution
2. Integration with engine and annotation modules
3. Focused only on local model inference
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import torch
from PIL import Image

from .annotation import annotate_image, format_predictions_for_api_compatibility
from .engine import get_yolo_model, predict_ui_elements


class LocalOmniParser:
    """
    Local OmniParser implementation for UI element detection and annotation.

    This class uses local YOLO models to detect and annotate UI elements in images.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the LocalOmniParser with model configurations.

        Args:
            config: Dictionary containing model paths and configurations.
                   If None, uses default configuration.
        """
        # Default configuration
        default_config = {
            "som_model_path": "/Users/nharada/Models/omniparser/model.pt",
            "box_threshold": 0.05,
            "iou_threshold": 0.1,
            "imgsz": 640,
        }

        self.config = {**default_config, **(config or {})}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initialize models
        self._load_models()

        logging.debug(f"LocalOmniParser initialized on {self.device}!")

    def _load_models(self):
        """Load the required models."""
        # Load YOLO model for icon detection
        self.yolo_model = get_yolo_model(model_path=self.config["som_model_path"])

    def predict(
        self,
        image: str | Image.Image | np.ndarray,
        **annotation_kwargs,
    ) -> dict:
        """
        Predict UI elements in the image and return annotated image.

        Args:
            image: Input image as file path, PIL Image, or numpy array
            **annotation_kwargs: Additional arguments for annotation (thickness, text_scale, etc.)

        Returns:
            Dictionary containing:
            - 'boxes': List of bounding boxes in format [x1, y1, x2, y2]
            - 'labels': List of element labels/descriptions
            - 'coordinates': Dictionary mapping element IDs to coordinates
            - 'parsed_content': List of parsed content descriptions
            - 'image_size': Tuple of (width, height)
            - 'annotated_image': PIL Image with annotations
        """
        # Get UI element predictions
        predictions = predict_ui_elements(
            image=image,
            model=self.yolo_model,
            box_threshold=self.config["box_threshold"],
            iou_threshold=self.config["iou_threshold"],
            imgsz=self.config["imgsz"],
            scale_img=True,
        )

        # Format predictions for API compatibility
        result = format_predictions_for_api_compatibility(
            predictions, predictions["image_size"]
        )

        # Add annotated image
        annotated_image = annotate_image(image, predictions, **annotation_kwargs)
        result["annotated_image"] = annotated_image

        return result

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