"""Auto-generated stub for module: data_prep."""
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from matrice_data_processing.pipeline import Pipeline
from matrice_data_processing.server_utils import download_file, chunk_items, get_number_of_dataset_batches, get_data_prep_batch_video_dataset_items, get_batch_dataset_items
from queue import Queue
from urllib.parse import urlparse
import csv
import cv2
import json
import logging
import os
import random
import shutil
import threading
import time
import uuid
import yaml

# Functions
def check_image_validity(local_filename: str, frame_num: int) -> Optional[str]: ...
    """
    Helper function to validate downloaded image files.
    
    Args:
        local_filename: Path to the downloaded file
        frame_num: Frame number for logging
    
    Returns:
        Local filename if valid, None otherwise
    """
def convert_bbox_coco2yolo(img_width: int, img_height: int, bbox: List[float]) -> List[float]: ...
    """
    Convert COCO format bounding box to YOLO format.
    
        Args:
            img_width: Width of image
            img_height: Height of image
            bbox: Bounding box in COCO format [x,y,w,h]
    
        Returns:
            Bounding box in YOLO format [x_center,y_center,w,h]
    """
def create_video_from_frames_mscoco(dataset_item: Dict, base_dataset_path: str, dataset_version: str) -> None: ...
    """
    Creates a video for each dataset item using its frames with safe threading and unique naming.
    
    This function handles cases where multiple dataset items share the same video name but belong
    to different splits by incorporating the dataset item ID into the filename for uniqueness.
    It also implements thread-safe operations to prevent race conditions during concurrent processing.
    
    Args:
        dataset_item (Dict): Contains '_id', 'fileInfo', etc.
        base_dataset_path (str): Base path to save videos.
        dataset_version (str): Version of the dataset used to determine split type.
    """
def dataset_items_producer(rpc: Any, dataset_id: str, dataset_version: str, pipeline_queue: Any, request_batch_size: int = 1000, processing_batch_size: int = 10) -> None: ...
    """
    Get items for a partition and add them to the pipeline queue.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            dataset_version: Dataset version
            pipeline_queue: Queue to add items to
            request_batch_size: Number of items to fetch per API request
            processing_batch_size: Size of batches to add to pipeline queue
    """
def detect_and_convert_bbox_format(img_width: int, img_height: int, bbox: List[float]) -> List[float]: ...
    """
    Detect bbox format and convert to YOLO format.
    
        Supports multiple bbox formats:
        - COCO: [x, y, width, height] (top-left + size)
        - XYXY: [x1, y1, x2, y2] (two corners)
        - Already normalized: values between 0-1
    
        Args:
            img_width: Width of image
            img_height: Height of image
            bbox: Bounding box in any supported format
    
        Returns:
            Bounding box in YOLO format [x_center,y_center,w,h] (normalized)
    """
def download_davis_yolo_frames(dataset_item: Dict, base_dataset_path: str, dataset_version: str, frame_split_map: Optional[Dict[Tuple[str, str], str]] = None) -> None: ...
def download_frame_with_retry(cloud_path: str, local_path: str, frame_num: int, max_retries: int = 5, timeout: int = 60) -> Optional[str]: ...
    """
    Download a frame with retry logic and enhanced validation.
    
    Args:
        cloud_path: Cloud storage path
        local_path: Local destination path
        frame_num: Frame number for logging
        max_retries: Maximum number of retry attempts
        timeout: Timeout for download in seconds
    
    Returns:
        Local path if successful, None otherwise
    """
def download_images(dataset_items: List[Dict], input_format: str, base_dataset_path: str, dataset_version: str) -> List[Dict]: ...
    """
    Download images for dataset items.
    
        Args:
            dataset_items: List of dataset items
            input_format: Format of dataset
            base_dataset_path: Base path to save images
            dataset_version: Dataset version
    
        Returns:
            List of successfully downloaded items
    """
def download_segment_videos(dataset_items: List[Dict], input_format: str, base_dataset_path: str, dataset_version: str) -> List[Dict]: ...
def extract_video_name_from_url(url: str) -> str: ...
    """
    Extracts video name from the frame's URL path.
    """
def get_categories_id_map(dataset_items: List[Dict], start_id: int = 0) -> Dict[str, int]: ...
    """
    Get mapping of categories to IDs.
    
        Args:
            dataset_items: List of dataset items
            start_id: Starting ID for categories
    
        Returns:
            Dictionary mapping category names to IDs
    """
def get_category_name(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get category name from dataset item annotations.
    """
def get_data_prep_pipeline(rpc: Any, dataset_id: str, dataset_version: str, input_format: str, base_dataset_path: str) -> Any: ...
    """
    Get the data prep pipeline.
    
        Args:
            rpc: RPC client
            dataset_id: Dataset ID
            dataset_version: Dataset version
            input_format: Format of annotations
            base_dataset_path: Base path to save dataset
    
        Returns:
            Configured Pipeline object
    """
def get_image_annotations(dataset_item: Dict, dataset_version: str = 'v1.0') -> List[Dict]: ...
    """
    Get annotations for a dataset item.
    """
def get_image_path(base_dataset_path: str, dataset_item: Dict, input_format: str, dataset_version: str) -> str: ...
    """
    Get save path for an image.
    
        Args:
            base_dataset_path: Base path to save dataset
            dataset_item: Dataset item containing image info
            input_format: Format of dataset
            dataset_version: Dataset version
    
        Returns:
            Full path where image should be saved
    """
def get_item_set_type(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get the set type (train/test/val) for a dataset item.
    """
def get_kinetics_annotations(dataset_item: Dict, dataset_version: str = 'v1.0') -> List[Dict]: ...
    """
    Get annotations for a dataset item.
    """
def get_kinetics_category_name(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get category name from dataset item annotations.
    """
def get_mscoco_annotations(dataset_items: List[Dict], categories_id_map: Dict[str, int]) -> List[Dict]: ...
    """
    Extract MSCOCO annotations from dataset items.
    
        Args:
            dataset_items: List of dataset items
            categories_id_map: Dictionary mapping categories to IDs
    
        Returns:
            List of annotation dictionaries in MSCOCO format
    """
def get_mscoco_categories(categories_id_map: Dict[str, int]) -> List[Dict]: ...
    """
    Extract MSCOCO categories from dataset items.
    
        Args:
            categories_id_map: Dictionary mapping categories to IDs
    
        Returns:
            List of category dictionaries in MSCOCO format
    """
def get_mscoco_images(dataset_items: List[Dict]) -> List[Dict]: ...
    """
    Extract MSCOCO images from dataset items.
    
        Args:
            dataset_items: List of dataset items
    
        Returns:
            List of image dictionaries in MSCOCO format
    """
def get_optimal_video_params(target_width: int, target_height: int, fps: float) -> dict: ...
    """
    Get optimal video encoding parameters based on dimensions and FPS.
    
    Args:
        target_width: Video width
        target_height: Video height
        fps: Frames per second
    
    Returns:
        Dictionary with optimal video parameters
    """
def get_video_data_prep_pipeline(rpc: Any, dataset_id: str, dataset_version: str, input_format: str, base_dataset_path: str) -> Any: ...
    """
    Get the data prep pipeline.
    
        Args:
            rpc: RPC client
            dataset_id: Dataset ID
            dataset_version: Dataset version
            input_format: Format of annotations
            base_dataset_path: Base path to save dataset
    
        Returns:
            Configured Pipeline object
    """
def get_video_item_set_type(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get the set type (train/test/val) for a dataset item.
    """
def get_video_save_path(base_dataset_path: str, dataset_item: Dict, input_format: str, dataset_version: str) -> str: ...
    """
    Get save path for an image or video.
    
        Args:
            base_dataset_path: Base path to save dataset
            dataset_item: Dataset item containing media info
            input_format: Format of dataset
            dataset_version: Dataset version
    
        Returns:
            Full path where media should be saved
    """
def map_frames_to_split(response_dict: Any) -> Any: ...
    """
    Given a dictionary with keys 'fileInfoResponse' and 'annotationResponse',
    return a mapping from unique frame key to its split.
    
    Unique frame key format: "<_idDataset>_<idVideoDatasetItem>_<sequenceNum>_<frameNum>"
    
    Args:
        response_dict (dict): {
            "fileInfoResponse": [dict, ...],
            "annotationResponse": [dict, ...]
        }
    
    Returns:
        dict: Mapping from unique frame ID to split (e.g., 'train', 'val', 'test').
    """
def process_final_annotations(dataset_items: List[List[Dict]], base_dataset_path: str, input_format: str, dataset_version: str) -> None: ...
    """
    Process final annotations after pipeline completion.
    
        Args:
            dataset_items: List of dataset items to process
            base_dataset_path: Base path to save dataset files
            input_format: Format of annotations (YOLO/COCO)
            dataset_version: Dataset version
    """
def segment_and_split_by_category(dataset_items: List[Dict], n_frames_per_segment: int = 2, split_ratios: Tuple[float, float, float] = (0.8, 0.1, 0.1), seed: int = 42) -> Dict[str, str]: ...
    """
    Returns a mapping of frame IDs (video_id + frame_id) to split types.
    Groups frames category-wise into segments of n frames,
    then splits them into train/val/test.
    """
def video_dataset_items_producer(rpc: Any, dataset_id: str, dataset_version: str, pipeline_queue: Any, request_batch_size: int = 50, processing_batch_size: int = 1, input_type: str = 'davis') -> None: ...
    """
    Get items for a partition and add them to the pipeline queue.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            dataset_version: Dataset version
            pipeline_queue: Queue to add items to
            request_batch_size: Number of items to fetch per API request
            processing_batch_size: Size of batches to add to pipeline queue
            input_type: Type of input data format
    """
def write_data_yaml(categories_id_map: Dict[str, int], yaml_file_path: str) -> None: ...
    """
    Write category data to YAML file.
    
        Args:
            categories_id_map: Dictionary mapping categories to IDs
            yaml_file_path: Path to save YAML file
    """
def write_davis_yolo_annotations(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
def write_kinetics_labels(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
    """
    Write Kinetics format labels (CSV) for videos.
    
    Args:
        local_path: Base path to save annotations.
        dataset_items: List of dataset items (videos).
        dataset_version: Dataset version (e.g., v1.0).
    """
def write_mscoco_annotation_file(dataset_items: List[Dict], categories_id_map: Dict[str, int], ann_json_path: str) -> None: ...
    """
    Write MSCOCO annotation file in COCO format.
    
        Args:
            dataset_items: List of dataset items
            categories_id_map: Dictionary mapping categories to IDs
            ann_json_path: Path to save annotation file
    """
def write_mscoco_annotation_files(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
    """
    Write MSCOCO annotation files for different itemSetTypes.
    
        Args:
            local_path: Base path to save annotation files
            dataset_items: List of dataset items
            dataset_version: Dataset version
    """
def write_video_coco_annotations(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
def write_yolo_labels(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
    """
    Write YOLO format labels for images.
    
        Args:
            local_path: Base path to save labels
            dataset_items: List of dataset items
            dataset_version: Dataset version
    """

# Classes
class DataPrep:
    """
    Class to handle dataset preparation.
    """

    def __init__(self: Any, session: Any, action_record_id: str) -> None: ...
        """
        Initialize DataPrep.
        
                Args:
                    session: Session object with RPC client
                    action_record_id: ID of action record
        """

    def start_processing(self: Any) -> None: ...
        """
        Start dataset preparation processing.
        """

    def update_status(self: Any, step_code: str, status: str, status_description: str, dataset_path: str = None, sample_count: int = None) -> None: ...
        """
        Update status of data preparation.
        
                Args:
                    step_code: Code indicating current step
                    status: Status of step
                    status_description: Description of status
                    dataset_path: Optional path to dataset
                    sample_count: Optional count of samples
        """

