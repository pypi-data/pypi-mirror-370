"""Auto-generated stub for module: aug_server_v2."""
from typing import Any, Dict, List, Optional

from PIL import Image
from abc import ABC, abstractmethod
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from matrice_common.utils import dependencies_check
from matrice_data_processing.augmentation_utils.strategies import *
from pydantic import BaseModel
import atexit
import base64
import cv2
import httpx
import io
import logging
import numpy as np
import signal
import threading
import time
import time
import urllib.request
import uvicorn

# Classes
class AugmentationRequest(BaseModel):
    """
    Request model for augmentation endpoint.
    """

    pass
class AugmentationResponse(BaseModel):
    """
    Response model for augmentation endpoint.
    """

    pass
class AugmentationServer:
    """
    Class to handle dataset augmentation server.
    """

    def __init__(self: Any, session: Any, action_record_id: str, port: int, ip_address: str = None) -> None: ...

    def start_server(self: Any) -> None: ...
        """
        Start the augmentation server.
        """

    def stop_server(self: Any) -> None: ...
        """
        Stop the augmentation server gracefully.
        """

    def update_server_address(self: Any, status: Any, port: Any, host: Any) -> None: ...
        """
        Update server address in the backend.
        """

    def update_status(self: Any, stepCode: str, status: str, status_description: str) -> None: ...
        """
        Update status of augmentation server.
        """

    def wait_for_shutdown(self: Any) -> None: ...
        """
        Wait for the server to be shut down.
        """

class AugmentationStep:
    """
    Represents a single augmentation step.
    """

    pass
class AugmentationStrategyFactory:
    """
    Factory class to create augmentation strategy instances.
    """

    STRATEGIES: Dict[Any, Any]

    def create_strategy(cls: Any, aug_step: Any) -> Any: ...

class ImageAugmentationStrategy(ABC):
    def __init__(self: Any, **kwargs: Any) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Any: ...

