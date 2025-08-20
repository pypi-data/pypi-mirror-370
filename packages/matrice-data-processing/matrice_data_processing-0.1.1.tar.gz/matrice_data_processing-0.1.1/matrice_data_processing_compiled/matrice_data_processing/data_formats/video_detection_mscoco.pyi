"""Auto-generated stub for module: video_detection_mscoco."""
from typing import Any, List

from collections import defaultdict
from matrice_data_processing.server_utils import get_corresponding_split_type, generate_short_uuid
from uuid import uuid4
import cv2
import json
import logging
import os
import requests
import tempfile

# Functions
def add_video_mscoco_dataset_items_details(batch_dataset_items: Any, frames_details: Any) -> Any: ...
    """
    Add MSCOCO video-style annotation details to frame-wise dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to enhance
            frames_details: Complete videos dictionary from get_video_mscoco_annotations()
    
        Returns:
            List of processed dataset items with annotation and video metadata
    """
def extract_video_identifier(path: Any) -> Any: ...
    """
    Extract the video name from the file path.
    
        Args:
            path: File path to extract video identifier from
    
        Returns:
            Video identifier string or None if path is invalid
    """
def get_video_metadata(presigned_url: Any) -> Any: ...
    """
    Downloads a video from a presigned URL, extracts its dimensions (width, height),
    FPS, and duration, and saves the first frame as an image locally.
    
    Args:
        presigned_url (str): The presigned URL of the video.
    
    Returns:
        dict: {
            "width": video_width,
            "height": video_height,
            "fps": rounded_fps,
            "first_frame_path": path_to_saved_image
        }
    """
def get_video_mscoco_annotations(annotation_paths: Any) -> Any: ...
    """
    Process MSCOCO-style video dataset annotations and return frame-based annotations grouped
        by split and video, using nested dictionary structure similar to YouTube BB function.
    """
