"""Auto-generated stub for module: video_imagenet_classification."""
from typing import Any, List, Tuple

from matrice_data_processing.server_utils import generate_short_uuid
from matrice_data_processing.server_utils import get_corresponding_split_type
from uuid import uuid4
import cv2
import cv2
import logging
import logging
import os
import os
import requests
import requests
import tempfile
import tempfile

# Functions
def add_video_imagenet_dataset_items_details(batch_dataset_items: Any) -> Any: ...
    """
    Add details to video imagenet dataset items.
    
        Args:
            batch_dataset_items: Batch of dataset items to process
    
        Returns:
            List of processed dataset items
    """
def get_imagenet_dataset_item_details(image_path: Any) -> Any: ...
    """
    Extract details from image path for ImageNet dataset.
    
        Args:
            image_path: Path to the image file
    
        Returns:
            Tuple of (split, category, annotations)
    """
def get_video_metadata(presigned_url: Any) -> Any: ...
    """
    Downloads a video from a presigned URL, extracts its dimensions (width, height),
    FPS, duration, and saves the first frame as an image locally.
    
    Args:
        presigned_url (str): The presigned URL of the video.
    
    Returns:
        dict: {
            "width": video_width,
            "height": video_height,
            "fps": rounded_fps,
            "duration": [0, duration],  # Video duration in seconds
            "first_frame_path": path_to_saved_image
        }
    """
