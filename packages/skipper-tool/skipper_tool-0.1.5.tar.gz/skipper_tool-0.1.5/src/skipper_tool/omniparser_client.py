#!/usr/bin/env python3
"""
OmniParser Client class that supports both local YOLO execution and remote API calls.

This class provides a unified interface for:
1. Local execution using YOLO models
2. Remote execution via API calls to the Modal-hosted OmniParser service
"""

import base64
import io
import json
import os

import numpy as np
from loguru import logger
import requests
from PIL import Image

# Import local OmniParser only when needed
try:
    from skipper_tool.omniparser import OmniParser

    LOCAL_OMNIPARSER_AVAILABLE = True
except ImportError:
    LOCAL_OMNIPARSER_AVAILABLE = False
    logger.warning("Local OmniParser not available. Only remote API mode will work.")


def _ensure_pil_image(image: str | Image.Image | np.ndarray) -> Image.Image:
    """Convert input to PIL Image if needed. Reusable utility function."""
    if isinstance(image, str):
        return Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        return Image.fromarray(image)
    elif isinstance(image, Image.Image):
        return image.convert("RGB")
    else:
        raise ValueError("Input must be a file path, PIL Image, or numpy array")


def _prepare_image_for_upload(
    image: str | Image.Image | np.ndarray,
) -> tuple[dict, Image.Image]:
    """Convert image to format suitable for API upload. Returns (files_dict, pil_image)."""
    pil_image = _ensure_pil_image(image)

    # Convert image to bytes for upload
    img_bytes = io.BytesIO()
    pil_image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    files = {"file": ("image.png", img_bytes, "image/png")}
    return files, pil_image


def _make_api_request(
    api_url: str,
    endpoint: str,
    api_key: str,
    files: dict,
    params: dict,
    timeout: int = 30,
) -> dict:
    """Make a POST request to the API and return the JSON response."""
    headers = {"X-API-Key": api_key}

    try:
        response = requests.post(
            f"{api_url}/{endpoint}",
            files=files,
            headers=headers,
            params=params,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Remote API request failed: {e}")
        raise Exception(f"Failed to get response from remote API: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {e}")
        raise Exception(f"Invalid response from remote API: {e}")


class OmniParserClient:
    """
    Client for OmniParser that supports both local and remote execution.

    Usage:
    # Local mode (if YOLO model path provided)
    client = OmniParserClient(yolo_model_path="/path/to/model.pt")

    # Remote mode (fallback when no model path or local mode fails)
    # Requires SKIPPER_API_KEY environment variable
    client = OmniParserClient()
    """

    def __init__(
        self,
        yolo_model_path: str | None = None,
        config: dict | None = None,
        skipper_config: dict | None = None,
    ):
        """
        Initialize the OmniParser client.

        Args:
            yolo_model_path: Optional path to local YOLO model. If provided, will use local execution.
                           If None or local execution fails, will fallback to remote API.
            config: Configuration dict for local OmniParser (ignored for remote)
            skipper_config: Skipper configuration dict containing API keys and URLs
        """
        self.yolo_model_path = yolo_model_path
        self.config = config or {}
        self.skipper_config = skipper_config or {}

        # Get API configuration from skipper config or environment variables
        from skipper_tool.config import get_api_key

        self.api_key = (
            get_api_key(self.skipper_config, "skipper_api_key", "SKIPPER_API_KEY")
            if self.skipper_config
            else os.getenv("SKIPPER_API_KEY")
        )
        self.api_url = self.skipper_config.get("api", {}).get(
            "skipper_api_url"
        ) or os.getenv(
            "SKIPPER_API_URL", "https://nate-3--omni-parser-api-fastapi-app.modal.run"
        ).rstrip("/")

        self.local_parser = None
        self.mode = None

        # Try local mode first if model path is provided
        if yolo_model_path and LOCAL_OMNIPARSER_AVAILABLE:
            try:
                local_config = {"som_model_path": yolo_model_path, **self.config}
                self.local_parser = OmniParser(config=local_config)
                self.mode = "local"
                logger.info(
                    f"OmniParserClient initialized in local mode with model: {yolo_model_path}"
                )
                return
            except Exception as e:
                logger.warning(
                    f"Failed to initialize local OmniParser: {e}. Falling back to remote API."
                )

        # Fall back to remote mode
        if not self.api_key:
            raise ValueError(
                "No Skipper API key found and local mode unavailable. "
                "Set SKIPPER_API_KEY environment variable, add skipper_api_key to your .skipperrc config file, or provide a valid yolo_model_path."
            )

        self.mode = "remote"
        logger.info(
            f"OmniParserClient initialized in remote mode with API: {self.api_url}"
        )

    def predict(
        self,
        image: str | Image.Image | np.ndarray,
        conf: float = 0.05,
        imgsz: int | None = None,
        iou_threshold: float = 0.9,
        scale_img: bool = False,
        output_coord_in_ratio: bool = False,
    ) -> dict:
        """
        Predict UI elements in the image using either local or remote execution.

        Args:
            image: Input image as file path, PIL Image, or numpy array
            conf: Confidence threshold for detections
            imgsz: Image size for processing
            iou_threshold: IoU threshold for non-maximum suppression
            scale_img: Whether to scale image during processing
            output_coord_in_ratio: Whether to output coordinates as ratios

        Returns:
            Dictionary containing:
            - 'boxes': List of bounding boxes in format [x1, y1, x2, y2]
            - 'labels': List of element labels/descriptions
            - 'coordinates': Dictionary mapping element IDs to coordinates
            - 'parsed_content': List of parsed content descriptions
            - 'image_size': Tuple of (width, height)
        """
        if self.mode == "local":
            return self._predict_local(image)
        else:
            return self._predict_remote(
                image, conf, imgsz, iou_threshold, scale_img, output_coord_in_ratio
            )

    def annotate(
        self,
        image: str | Image.Image | np.ndarray,
        predictions: dict | None = None,
        **kwargs,
    ) -> Image.Image:
        """
        Annotate image with bounding boxes.

        Args:
            image: Input image
            predictions: Predictions from predict() method. If None, will run predict()
            **kwargs: Additional arguments for annotation (local mode only)

        Returns:
            PIL Image with annotations
        """
        if self.mode == "local":
            return self.local_parser.annotate(image, predictions, **kwargs)
        else:
            return self._annotate_remote(image, **kwargs)

    def _predict_local(self, image: str | Image.Image | np.ndarray) -> dict:
        """Execute prediction using local OmniParser."""
        return self.local_parser.predict(image)

    def _predict_remote(
        self,
        image: str | Image.Image | np.ndarray,
        conf: float = 0.05,
        imgsz: int | None = None,
        iou_threshold: float = 0.9,
        scale_img: bool = False,
        output_coord_in_ratio: bool = False,
    ) -> dict:
        """Execute prediction using remote API."""
        # Prepare image for upload
        files, pil_image = _prepare_image_for_upload(image)

        # Prepare request parameters
        params = {
            "conf": conf,
            "iou_threshold": iou_threshold,
            "scale_img": scale_img,
            "output_coord_in_ratio": output_coord_in_ratio,
        }

        # Add imgsz if specified
        if imgsz is not None:
            params["imgsz"] = imgsz

        # Make API request
        result = _make_api_request(self.api_url, "detect", self.api_key, files, params)

        # Ensure the result has the expected format
        return {
            "boxes": result.get("boxes", []),
            "labels": result.get("labels", []),
            "coordinates": result.get("coordinates", {}),
            "parsed_content": result.get("parsed_content", []),
            "image_size": result.get("image_size", list(pil_image.size)),
        }

    def _annotate_remote(
        self,
        image: str | Image.Image | np.ndarray,
        conf: float = 0.05,
        imgsz: int | None = None,
        iou_threshold: float = 0.9,
        scale_img: bool = False,
        thickness: int = 3,
        text_scale: float = 0.8,
    ) -> Image.Image:
        """Execute annotation using remote API."""
        # Prepare image for upload
        files, _ = _prepare_image_for_upload(image)

        # Prepare request parameters
        params = {
            "conf": conf,
            "iou_threshold": iou_threshold,
            "scale_img": scale_img,
            "thickness": thickness,
            "text_scale": text_scale,
        }

        # Add imgsz if specified
        if imgsz is not None:
            params["imgsz"] = imgsz

        # Make API request
        result = _make_api_request(
            self.api_url, "annotate", self.api_key, files, params
        )

        # Decode the base64 encoded annotated image
        encoded_image = result.get("annotated_image")
        if not encoded_image:
            raise Exception("No annotated image returned from API")

        try:
            image_bytes = base64.b64decode(encoded_image)
            annotated_image = Image.open(io.BytesIO(image_bytes))
            return annotated_image
        except Exception as e:
            logger.error(f"Failed to decode annotated image: {e}")
            raise Exception(f"Failed to process annotated image: {e}")

    def health_check(self) -> dict:
        """
        Check the health of the service.

        Returns:
            Dictionary with health status
        """
        if self.mode == "local":
            return {"status": "ok", "mode": "local", "model_path": self.yolo_model_path}
        else:
            try:
                response = requests.get(
                    f"{self.api_url}/health",
                    headers={"X-API-Key": self.api_key},
                    timeout=10,
                )
                response.raise_for_status()
                result = response.json()
                result["mode"] = "remote"
                return result
            except Exception as e:
                return {"status": "error", "mode": "remote", "error": str(e)}
