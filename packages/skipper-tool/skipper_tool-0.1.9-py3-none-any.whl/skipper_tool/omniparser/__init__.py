#!/usr/bin/env python3
"""
OmniParser package for UI element detection and annotation.

This package provides a unified interface for both local YOLO execution
and remote API calls for UI element detection in images.

Main exports:
- OmniParser: Unified client with automatic local/remote selection
- LocalOmniParser: Local YOLO-based implementation
- RemoteOmniParser: Remote API-based implementation

Usage:
    from skipper_tool.omniparser import OmniParser

    # Auto-selection (tries local first, falls back to remote)
    parser = OmniParser()

    # Force local mode (if YOLO model path provided)
    parser = OmniParser(yolo_model_path="/path/to/model.pt")

    # Force remote mode
    parser = OmniParser(force_remote=True)

    # Use the parser
    result = parser.predict("screenshot.png")
"""

from .client import OmniParser
from .local import LocalOmniParser
from .remote import RemoteOmniParser

# For backward compatibility, also export some common functions
from .annotation import annotate_image, ensure_pil_image
from .engine import get_yolo_model, predict_ui_elements

__all__ = [
    "OmniParser",
    "LocalOmniParser",
    "RemoteOmniParser",
    "annotate_image",
    "ensure_pil_image",
    "get_yolo_model",
    "predict_ui_elements",
]
