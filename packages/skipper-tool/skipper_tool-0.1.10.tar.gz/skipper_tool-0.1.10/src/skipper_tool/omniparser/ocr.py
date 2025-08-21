#!/usr/bin/env python3
"""
OCR utilities for text detection in UI screenshots.

This module provides PaddleOCR-based text detection functionality
adapted from the Magma UI agent demo.
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple, List

# Initialize PaddleOCR with optimized settings from Magma demo
from paddleocr import PaddleOCR

_paddle_ocr = PaddleOCR(
    lang="en",
    use_angle_cls=False,
    use_gpu=False,
    show_log=False,
    max_batch_size=1024,
    use_dilation=True,  # Improves accuracy
    det_db_score_mode="slow",  # Improves accuracy
    rec_batch_num=1024,
)


def get_xyxy_from_paddle_result(
    coords: List[List[List[float]]],
) -> Tuple[int, int, int, int]:
    """Convert PaddleOCR coordinate format to xyxy bounding box.

    Args:
        coords: PaddleOCR coordinate format [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

    Returns:
        Tuple of (x1, y1, x2, y2) coordinates
    """
    x_coords = [point[0] for point in coords]
    y_coords = [point[1] for point in coords]
    x1, y1 = int(min(x_coords)), int(min(y_coords))
    x2, y2 = int(max(x_coords)), int(max(y_coords))
    return x1, y1, x2, y2


def check_ocr_box(
    image_source: Union[str, Image.Image],
    text_threshold: float = 0.5,
    output_bb_format: str = "xyxy",
) -> Tuple[Tuple[List[str], List[Tuple[int, int, int, int]]], None]:
    """
    Detect text in image using PaddleOCR.

    Args:
        image_source: Input image as file path or PIL Image
        text_threshold: Confidence threshold for text detection
        output_bb_format: Output bounding box format ('xyxy' or 'xywh')

    Returns:
        Tuple containing:
        - (text_list, bbox_list): Lists of detected text and bounding boxes
        - None: Goal filtering placeholder (for compatibility)

    Raises:
        ImportError: If PaddleOCR is not installed
        ValueError: If image format is not supported
    """
    if _paddle_ocr is None:
        raise ImportError(
            "PaddleOCR is not installed. Install it with: pip install paddleocr"
        )

    # Convert input to PIL Image if needed
    if isinstance(image_source, str):
        image_source = Image.open(image_source)
    elif not isinstance(image_source, Image.Image):
        raise ValueError("Input must be a file path or PIL Image")

    # Convert RGBA to RGB if needed
    if image_source.mode == "RGBA":
        image_source = image_source.convert("RGB")

    # Convert to numpy array for PaddleOCR
    image_np = np.array(image_source)

    # Run OCR detection
    result = _paddle_ocr.ocr(image_np, cls=False)[0]

    if result is None:
        return ([], []), None

    # Filter results by confidence threshold
    filtered_results = [item for item in result if item[1][1] > text_threshold]

    # Extract coordinates and text
    coords = [item[0] for item in filtered_results]
    text = [item[1][0] for item in filtered_results]

    # Convert coordinates to desired format
    if output_bb_format == "xyxy":
        bbox = [get_xyxy_from_paddle_result(coord) for coord in coords]
    elif output_bb_format == "xywh":
        xyxy_boxes = [get_xyxy_from_paddle_result(coord) for coord in coords]
        bbox = [(x1, y1, x2 - x1, y2 - y1) for x1, y1, x2, y2 in xyxy_boxes]
    else:
        raise ValueError("output_bb_format must be 'xyxy' or 'xywh'")

    return (text, bbox), None


def is_paddleocr_available() -> bool:
    """Check if PaddleOCR is available."""
    return _paddle_ocr is not None
