"""Auto-generated stub for module: video_server."""
from typing import Any, Dict, List, Optional

from matrice_data_processing.data_formats.video_mscoco_detection import get_msococo_videos_details, add_mscoco_video_dataset_items_details
from matrice_data_processing.data_formats.yolo_detection import convert_payload_to_coco_format
from matrice_data_processing.pipeline import Pipeline
from matrice_data_processing.server import get_annotation_files, partition_items_producer, batch_download_samples, batch_calculate_sample_properties, submit_partition_status
from matrice_data_processing.server_utils import get_unprocessed_partitions
from queue import Queue
import cv2
import logging
import os
import traceback

# Constants
TMP_FOLDER: Any

# Functions
def batch_update_video_dataset_items(batch_video_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, attempts: int = 3, is_yolo: bool = False) -> List[Dict[str, Any]]: ...
    """
    Update video dataset items in batch.
    
        Args:
            batch_video_details: List of video details to update
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            version: Version of the dataset
            attempts: Number of retry attempts
            is_yolo: Whether the dataset is in YOLO format
    
        Returns:
            List of updated dataset items
    """
def calculate_video_properties(video_details: Dict[str, Any]) -> Dict[str, Any]: ...
    """
    Calculate properties of a video.
    
        Args:
            video_details: Dictionary containing video metadata
    
        Returns:
            Updated video details with calculated properties
    """
def get_mscoco_video_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
    """
    Create and configure the processing pipeline.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            dataset_version: Version number of the dataset
            action_record_id: ID of the action record
    
        Returns:
            Configured Pipeline instance
    """
