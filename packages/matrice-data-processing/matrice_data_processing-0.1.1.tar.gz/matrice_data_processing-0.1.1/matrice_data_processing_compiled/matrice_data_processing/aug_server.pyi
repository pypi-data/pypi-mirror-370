"""Auto-generated stub for module: aug_server."""
from typing import Any, Dict, List, Optional

from PIL import Image
from fastapi import FastAPI, HTTPException
from matrice_common.utils import dependencies_check
from matrice_data_processing.image_augmentations import get_augmentation_compose
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
        """
        Initialize AugmentationServer.
        
                Args:
                    session: Session object with RPC client
                    action_record_id: ID of action record
                    port: Port to run the server on
                    ip_address: IP address to bind to (optional)
        """

    def start_server(self: Any) -> None: ...
        """
        Start the augmentation server.
        """

    def stop_server(self: Any) -> None: ...
        """
        Stop the augmentation server gracefully.
        """

    def update_server_address(self: Any) -> None: ...
        """
        Update server address in the backend.
        """

    def update_status(self: Any, stepCode: str, status: str, status_description: str) -> None: ...
        """
        Update status of augmentation server.
        
                Args:
                    stepCode: Code indicating current step
                    status: Status of step
                    status_description: Description of status
        """

    def wait_for_shutdown(self: Any) -> None: ...
        """
        Wait for the server to be shut down.
        """

