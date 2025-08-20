"""Auto-generated stub for module: server."""
from typing import Any, Dict, List, Optional

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from matrice_data_processing.client_utils import scan_folder
from matrice_data_processing.data_formats.imagenet_classification import add_imagenet_dataset_items_details
from matrice_data_processing.data_formats.labelbox_classification import get_labelbox_classification_image_details, add_labelbox_classification_dataset_items_details, add_labelbox_classification_dataset_item_local_file_path
from matrice_data_processing.data_formats.labelbox_detection import get_labelbox_image_details, add_labelbox_dataset_items_details, add_labelbox_dataset_item_local_file_path, download_labelbox_dataset_items
from matrice_data_processing.data_formats.mscoco_detection import get_msococo_images_details, add_mscoco_dataset_items_details
from matrice_data_processing.data_formats.pascalvoc_detection import get_pascalvoc_image_details, add_pascalvoc_dataset_items_details
from matrice_data_processing.data_formats.unlabelled import add_unlabelled_dataset_items_details
from matrice_data_processing.data_formats.video_davis_segmentation import get_davis_annotations, add_davis_dataset_items_details
from matrice_data_processing.data_formats.video_detection_mscoco import add_video_mscoco_dataset_items_details, get_video_mscoco_annotations
from matrice_data_processing.data_formats.video_imagenet_classification import add_video_imagenet_dataset_items_details
from matrice_data_processing.data_formats.video_kinetics_activity_recognition import get_kinetics_annotations, add_kinetics_dataset_items_details
from matrice_data_processing.data_formats.video_mot_tracking import get_mot_annotations, add_mot_dataset_items_details
from matrice_data_processing.data_formats.video_youtube_bb_tracking import get_youtube_bb_video_frame_details, add_youtube_bb_dataset_items_details
from matrice_data_processing.data_formats.yolo_detection import get_yolo_image_details, add_yolo_dataset_items_details, convert_payload_to_coco_format
from matrice_data_processing.pipeline import Pipeline
from matrice_data_processing.server_utils import download_file, rpc_get_call, get_batch_pre_signed_download_urls, get_filename_from_url, update_partition_status, update_video_frame_partition_status, get_unprocessed_partitions, extract_dataset, get_partition_items, chunk_items, handle_source_url_dataset_download, get_video_frame_partition_items
from queue import Queue
import logging
import logging
import os
import requests
import time
import time
import traceback

# Constants
TMP_FOLDER: Any

# Functions
def batch_calculate_sample_properties(batch_sample_details: List[Dict[str, Any]], properties_calculation_fn: Any) -> List[Dict[str, Any]]: ...
    """
    Calculate properties for a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
    
        Returns:
            List of processed image details
    """
def batch_download_samples(batch_image_details: List[Dict[str, Any]], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> List[Dict[str, Any]]: ...
    """
    Download a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
            rpc: RPC client for making API calls
    
        Returns:
            List of updated sample details
    """
def batch_download_video_samples(batch_image_details: List[Dict[str, Any]], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> List[Dict[str, Any]]: ...
    """
    Download a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
            rpc: RPC client for making API calls
    
        Returns:
            List of updated sample details
    """
def batch_update_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, attempts: int = 3, is_yolo: bool = False) -> List[Dict[str, Any]]: ...
    """
    Update dataset items in batch.
    
        Args:
            batch_image_details: List of dictionaries containing image details
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            version: Version of the dataset
            attempts: Number of retry attempts
            is_yolo: Whether using YOLO format
    
        Returns:
            Updated batch image details
    """
def batch_update_kinetics_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, attempts: int = 3, is_yolo: bool = False, batch_size: int = 30) -> List[Dict[str, Any]]: ...
    """
    Update dataset items in batch, processing frames in groups of 30.
    
        Args:
            batch_image_details: List of image details to update
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            version: Version of the dataset
            attempts: Number of retry attempts
            is_yolo: Whether the dataset is in YOLO format
            batch_size: Number of frames to process in one API call
    
        Returns:
            List of updated dataset items
    """
def batch_update_video_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, project_id: str, attempts: int = 3) -> List[Dict[str, Any]]: ...
    """
    Update video dataset items' metadata and annotations in batch with multithreading.
    
        Args:
            batch_image_details: List of dictionaries containing video details
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            version: Version of the dataset
            project_id: Project ID for segment annotations
            attempts: Number of retry attempts
    
        Returns:
            Updated batch image details with processing status
    """
def batch_update_video_davis_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, project_id: str, attempts: int = 3, batch_segment_limit: int = 10, frames_per_segment: int = 16) -> List[Dict[str, Any]]: ...
    """
    Update high-level video info and segment-wise annotations for DAVIS-style datasets.
    """
def batch_update_video_imagenet_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, attempts: int = 3, is_yolo: bool = False, batch_size: int = 30) -> List[Dict[str, Any]]: ...
    """
    Update dataset items in batch, processing frames in groups of 30.
    
        Args:
            batch_image_details: List of image details to update
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            version: Version of the dataset
            attempts: Number of retry attempts
            is_yolo: Whether the dataset is in YOLO format
            batch_size: Number of frames to process in one API call
    
        Returns:
            List of updated dataset items
    """
def batch_update_video_mot_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, project_id: str, attempts: int = 3, segments_per_request: int = 10) -> List[Dict[str, Any]]: ...
def batch_update_video_mscoco_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, project_id: str, attempts: int = 3, frames_per_segment: int = 16, batch_segment_limit: int = 10) -> List[Dict[str, Any]]: ...
    """
    Update video metadata and segment-wise annotations in MSCOCO to match DAVIS format.
    """
def batch_upload_video_samples(batch_image_details: List[Dict[str, Any]], rpc: Any, bucket_alias: str = '', account_number: str = '') -> List[Dict[str, Any]]: ...
    """
    Download a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
            rpc: RPC client for making API calls
    
        Returns:
            List of updated sample details
    """
def calculate_image_properties(image_details: Dict[str, Any]) -> Dict[str, Any]: ...
    """
    Calculate properties of an image.
    
        Args:
            image_details: Dictionary containing image metadata
    
        Returns:
            Updated image details with calculated properties
    """
def download_labelbox_dataset(dataset_id: Any, rpc: Any, dataset_version: Any, source_url: Any) -> Any: ...
    """
    Download a dataset from Labelbox.
    
        Args:
            dataset_id: ID of the dataset
            rpc: RPC client for making API calls
            dataset_version: Version of the dataset
            source_url: Optional source URL to download from
    
        Returns:
            Path to the downloaded dataset
    """
def download_samples(image_details: Dict[str, Any], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> Dict[str, Any]: ...
    """
    Download sample and update sample details.
    
        Args:
            image_details: Dictionary containing image metadata
            rpc: RPC client for making API calls
            bucket_alias: Bucket alias
            account_number: Account number
    
        Returns:
            Updated sample details dictionary
    """
def download_video_samples(image_details: Dict[str, Any], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> Dict[str, Any]: ...
    """
    Download sample and update sample details.
    
        Args:
            image_details: Dictionary containing image metadata
            rpc: RPC client for making API calls
            bucket_alias: Bucket alias
            account_number: Account number
    
        Returns:
            Updated sample details dictionary
    """
def get_annotation_files(rpc: Any, dataset_id: str, dataset_version: str, is_annotations_compressed: bool = False) -> List[str]: ...
    """
    Download and return paths to annotation files.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            is_annotations_compressed: Whether annotations are in compressed format
    
        Returns:
            List of local paths to downloaded annotation files
    """
def get_imagenet_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_kinetics_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_labelbox_classification_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '') -> Optional[Pipeline]: ...
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
def get_labelbox_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '') -> Optional[Pipeline]: ...
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
def get_mscoco_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_pascalvoc_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_pre_signed_upload_urls(cloud_file_paths: Any, rpc: Any, file_type: Any, bucket_alias: Any = '', account_number: Any = '') -> Any: ...
    """
    Get pre-signed upload URLs for files.
    
        Args:
            cloud_file_paths: Paths of files in cloud storage
            rpc: RPC client for making API calls
            file_type: Type of files
            bucket_alias: Bucket alias
            account_number: Account number
    
        Returns:
            Response from API containing pre-signed URLs
    """
def get_unlabelled_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_video_davis_segmentation_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_video_imagenet_classification_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_video_mot_tracking_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_video_mscoco_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_video_youtube_bb_tracking_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Optional[Pipeline]: ...
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
def get_yolo_server_processing_pipeline(rpc: Any, dataset_id: str, dataset_version: str, action_record_id: str, bucket_alias: str = '', account_number: str = '', project_id: str = '') -> Any: ...
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
def partition_items_producer(rpc: Any, dataset_id: str, partition: int, pipeline_queue: Any, download_images_required: bool = False, request_batch_size: int = 1000, processing_batch_size: int = 10) -> None: ...
    """
    Get items for a partition and add them to the pipeline queue.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            partition: Partition number
            pipeline_queue: Queue to add items to
            download_images_required: Whether to get presigned URLs for images
            request_batch_size: Number of items to fetch per API request
            processing_batch_size: Size of batches to add to pipeline queue
    """
def submit_partition_status(dataset_items_batches: List[List[Dict[str, Any]]], rpc: Any, action_record_id: str, dataset_id: str, version: str, annotation_type: str) -> None: ...
    """
    Submit status of processed partition.
    
        Args:
            dataset_items_batches: List of batches of dataset items
            rpc: RPC client for making API calls
            action_record_id: ID of the action record
            dataset_id: ID of the dataset
            version: Version of the dataset
            annotation_type: Type of annotation
    """
def submit_video_frame_partition_status(dataset_items_batches: List[List[Dict[str, Any]]], rpc: Any, action_record_id: str, dataset_id: str, version: str, annotation_type: str, sample_stats: Optional[Dict[str, Any]] = None) -> None: ...
    """
    Submit status updates for processed partitions.
    
        Args:
            dataset_items_batches: List of processed dataset item batches
            rpc: RPC client for making API calls
            action_record_id: ID of the action record
            dataset_id: ID of the dataset
            version: Version of the dataset
            annotation_type: Type of annotations
    """
def upload_file(local_path: Any, presigned_url: Any, max_attempts: Any = 5) -> Any: ...
    """
    Upload a file to a presigned URL.
    
        Args:
            local_path: Local path of the file to upload
            presigned_url: Pre-signed URL to upload to
            max_attempts: Maximum number of upload attempts
    
        Returns:
            Boolean indicating success of upload
    """
def upload_video_samples(image_details: Dict[str, Any], rpc: Any, bucket_alias: str = '', account_number: str = '') -> Dict[str, Any]: ...
    """
    Upload video samples to storage.
    
        Args:
            image_details: Dictionary with sample details
            rpc: RPC client for API calls
            bucket_alias: Bucket alias for private storage
            account_number: Account number for private storage
    
        Returns:
            Updated image details
    """
def video_frame_partition_items_producer(rpc: Any, dataset_id: str, partition: int, pipeline_queue: Any, download_images_required: bool = False, request_batch_size: int = 1000, processing_batch_size: int = 10, isFileInfoRequired: bool = True, input_type: str = 'mscoco_video') -> None: ...
    """
    Get items for a partition and add them to the pipeline queue.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: ID of the dataset
            partition: Partition number
            pipeline_queue: Queue to add items to
            download_images_required: Whether to get presigned URLs for images
            request_batch_size: Number of items to fetch per API request
            processing_batch_size: Size of batches to add to pipeline queue
    """
