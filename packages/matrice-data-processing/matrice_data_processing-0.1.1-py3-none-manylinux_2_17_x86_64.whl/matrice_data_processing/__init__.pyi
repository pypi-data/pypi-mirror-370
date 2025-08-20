"""Auto-generated stubs for package: matrice_data_processing."""
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from PIL import Image
from abc import ABC, abstractmethod
from augmentation_utils.base import ImageAugmentationStrategy
from augmentation_utils.strategies import *
from augmentation_utils.strategies import BlurAugmentation, BrightnessContrastAugmentation, HorizontalFlipAugmentation, RandomAffineAugmentation, ColorJitterAugmentation, HueSaturationValueAugmentation
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from fastapi import FastAPI, HTTPException
from image_data_augmentation import create_probability_based_augmentation_pipeline, parse_dynamic_pipeline_config, DynamicPipelineConfig, AugmentationStep
from kafka import KafkaConsumer, KafkaProducer
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from kafka import KafkaProducer, KafkaConsumer
from math import comb
from matrice.dataset import Dataset
from matrice.dataset import get_dataset_size_in_mb_from_url
from matrice.projects import Projects
from matrice_common.utils import dependencies_check
from matrice_data_processing.augmentation_utils.strategies import *
from matrice_data_processing.client import add_batch_presigned_upload_urls, upload_batch_files
from matrice_data_processing.client import handle_client_processing_pipelines, handle_client_video_processing_pipelines
from matrice_data_processing.client import handle_client_processing_pipelines, handle_client_video_processing_pipelines, get_partition_status, get_video_partition_status
from matrice_data_processing.client_utils import ANNOTATION_PARTITION_TYPE, SAMPLES_PARTITION_TYPE, scan_dataset, get_annotations_partition, get_images_partitions, get_youtube_bb_partitions, get_cloud_file_path, update_annotation_bucket_url, get_batch_pre_signed_upload_urls, upload_file, compress_annotation_files, update_partitions_numbers, create_partition_stats, get_youtube_bb_relative_path, get_mot_partitions, get_video_mot_cloud_file_path, get_video_mscoco_cloud_file_path, get_davis_partitions, get_davis_relative_path, get_video_imagenet_partitions, get_kinetics_partitions, get_video_mscoco_partitions, create_video_blank_dataset_items, extract_frames_from_videos, restructure_davis_dataset
from matrice_data_processing.client_utils import get_size_mb, upload_compressed_dataset, is_file_compressed, complete_dataset_items_upload, get_youtube_bb_partitions, get_mot_partitions, get_davis_partitions, get_video_imagenet_partitions, get_kinetics_partitions, get_video_mscoco_partitions, extract_frames_from_videos, scan_dataset
from matrice_data_processing.client_utils import is_file_compressed
from matrice_data_processing.client_utils import scan_folder
from matrice_data_processing.client_utils import update_partitions_numbers, create_partition_stats, SAMPLES_PARTITION_TYPE
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
from matrice_data_processing.data_formats.video_mscoco_detection import get_msococo_videos_details, add_mscoco_video_dataset_items_details
from matrice_data_processing.data_formats.video_youtube_bb_tracking import get_youtube_bb_video_frame_details, add_youtube_bb_dataset_items_details
from matrice_data_processing.data_formats.yolo_detection import convert_payload_to_coco_format
from matrice_data_processing.data_formats.yolo_detection import get_yolo_image_details, add_yolo_dataset_items_details, convert_payload_to_coco_format
from matrice_data_processing.data_prep import dataset_items_producer
from matrice_data_processing.data_prep import dataset_items_producer, get_item_set_type
from matrice_data_processing.image_augmentations import get_augmentation_compose
from matrice_data_processing.pipeline import Pipeline
from matrice_data_processing.server import batch_update_dataset_items
from matrice_data_processing.server import get_annotation_files, partition_items_producer, batch_download_samples, batch_calculate_sample_properties, submit_partition_status
from matrice_data_processing.server import get_mscoco_server_processing_pipeline, get_imagenet_server_processing_pipeline, get_pascalvoc_server_processing_pipeline, get_labelbox_server_processing_pipeline, get_yolo_server_processing_pipeline, get_unlabelled_server_processing_pipeline, get_labelbox_classification_server_processing_pipeline, handle_source_url_dataset_download, download_labelbox_dataset, get_video_youtube_bb_tracking_server_processing_pipeline, get_video_mot_tracking_server_processing_pipeline, get_video_davis_segmentation_server_processing_pipeline, get_video_imagenet_classification_server_processing_pipeline, get_kinetics_server_processing_pipeline, get_video_mscoco_server_processing_pipeline
from matrice_data_processing.server_utils import download_file, chunk_items, get_number_of_dataset_batches, get_data_prep_batch_video_dataset_items, get_batch_dataset_items
from matrice_data_processing.server_utils import download_file, generate_short_uuid
from matrice_data_processing.server_utils import download_file, rpc_get_call, get_batch_pre_signed_download_urls, get_filename_from_url, update_partition_status, update_video_frame_partition_status, get_unprocessed_partitions, extract_dataset, get_partition_items, chunk_items, handle_source_url_dataset_download, get_video_frame_partition_items
from matrice_data_processing.server_utils import generate_short_uuid, get_number_of_dataset_batches
from matrice_data_processing.server_utils import get_number_of_dataset_batches
from matrice_data_processing.server_utils import get_unprocessed_partitions
from matrice_inference.deploy.client import MatriceDeployClient
from matrice_inference.deployment import Deployment
from pipeline import Pipeline
from pydantic import BaseModel
from queue import Queue
from queue import Queue, Empty
from scipy.special import softmax
from urllib.parse import urlparse
import albumentations as A
import atexit
import base64
import csv
import cv2
import httpx
import io
import json
import logging
import math
import numpy as np
import os
import random
import requests
import shutil
import signal
import sys
import tarfile
import tempfile
import threading
import time
import traceback
import urllib.request
import uuid
import uvicorn
import yaml
import zipfile

# Constants
ANNOTATION_EXTENSIONS: List[Any] = ...  # From client_utils
ANNOTATION_PARTITION_TYPE: str = ...  # From client_utils
COMPRESSED_EXTENSIONS: List[Any] = ...  # From client_utils
MAX_PARTITION_SIZE_BYTES: Any = ...  # From client_utils
SAMPLES_EXTENSIONS: List[Any] = ...  # From client_utils
SAMPLES_PARTITION_TYPE: str = ...  # From client_utils
AUGMENTATIONS: Dict[Any, Any] = ...  # From image_augmentations
AUGMENTATIONS_CONFIG: Dict[Any, Any] = ...  # From image_augmentations
MIN_DIM: float = ...  # From image_data_augmentation
TMP_FOLDER: Any = ...  # From server
TMP_FOLDER: Any = ...  # From video_server

# Functions
# From client
def add_batch_presigned_upload_urls(batch: Any, rpc: Any, partition_type: Any, bucket_alias: Any = '', account_number: Any = '', project_id: Any = None) -> Any: ...

# From client
def add_video_batch_presigned_upload_urls(batch: Any, rpc: Any, partition_type: Any, bucket_alias: Any = '', account_number: Any = '') -> Any: ...

# From client
def add_video_imagenet_presigned_upload_urls(batch: Any, rpc: Any, partition_type: Any, bucket_alias: Any = '', account_number: Any = '') -> Any: ...

# From client
def batch_create_dataset_items(batch: Any, dataset_id: Any, dataset_version: Any, rpc: Any) -> Any: ...

# From client
def batch_create_video_dataset_items(batch: Any, dataset_id: Any, dataset_version: Any, project_id: Any, rpc: Any, input_type: Any = None, num_dataset_items: Any = 0, dataset_item_ids: Any = []) -> Any: ...

# From client
def batch_create_video_imagenet_dataset_items(batch: Any, dataset_id: Any, dataset_version: Any, project_id: Any, rpc: Any, input_type: Any = None) -> Any: ...

# From client
def batch_create_video_imagenet_items(batch: Any, dataset_id: Any, dataset_version: Any, project_id: Any, rpc: Any, input_type: Any = None) -> Any: ...

# From client
def batch_create_video_youtube_bb_dataset_items(batch: Any, dataset_id: Any, dataset_version: Any, project_id: Any, rpc: Any, input_type: Any = None, num_dataset_items: Any = 0, dataset_item_ids: Any = None) -> Any: ...

# From client
def get_client_annotations_processing_pipeline(annotations_partition: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, rpc: Any, compress_annotations: Any = False, max_attempts: Any = 5, batch_size: Any = 16, bucket_alias: Any = '', account_number: Any = '', project_id: Any = None) -> Any: ...

# From client
def get_client_images_processing_pipeline(images_partitions: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, rpc: Any, max_attempts: Any = 5, batch_size: Any = 16, bucket_alias: Any = '', account_number: Any = '', project_id: Any = None) -> Any: ...

# From client
def get_client_processing_pipelines(rpc: Any, dataset_id: Any, dataset_version: Any, images_partition_status: list, annotation_partition_status: list, dataset_path: str, is_annotations_compressed: bool, destination_bucket_alias: str, account_number: str, project_id: Any = None) -> Any: ...

# From client
def get_client_video_processing_pipeline(images_partitions: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, rpc: Any, project_id: Any, max_attempts: Any = 5, batch_size: Any = 16, bucket_alias: Any = '', account_number: Any = '', input_type: Any = 'youtube_bb', num_dataset_items: Any = 0) -> Any: ...

# From client
def get_client_video_processing_pipelines(project_id: Any, rpc: Any, dataset_id: Any, dataset_version: Any, images_partition_status: list, annotation_partition_status: list, dataset_path: str, is_annotations_compressed: bool, destination_bucket_alias: str, account_number: str, input_type: str = 'youtube_bb', num_dataset_items: int = 0) -> Any: ...

# From client
def get_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def get_partition_status(base_path: Any, skip_annotation_partition: Any = False) -> Any: ...

# From client
def get_video_davis_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def get_video_imagenet_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def get_video_kinetics_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def get_video_mot_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def get_video_mscoco_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def get_video_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def get_video_partition_status(base_path: Any, skip_annotation_partition: Any = False, get_partitions: Any = get_youtube_bb_partitions, rename_annotation_files: Any = False, input_type: Any = None) -> Any: ...

# From client
def get_video_youtube_bb_partition_batches(partition: Any, batch_size: Any, dataset_id: Any, dataset_version: Any, base_dataset_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client
def handle_client_processing_pipelines(rpc: Any, dataset_id: Any, source_dataset_version: Any, target_dataset_version: Any, input_type: Any, source_URL: Any = '', dataset_path: Any = '', destination_bucket_alias: Any = '', account_number: Any = '', skip_partition_status: Any = False, annotation_partition_status: Any = None, images_partition_status: Any = None, project_id: Any = None) -> Any: ...

# From client
def handle_client_video_processing_pipelines(project_id: Any, rpc: Any, dataset_id: Any, source_dataset_version: Any, target_dataset_version: Any, input_type: Any, source_URL: Any = '', dataset_path: Any = '', destination_bucket_alias: Any = '', account_number: Any = '', skip_partition_status: Any = False, annotation_partition_status: Any = None, images_partition_status: Any = None, unique_videos: Any = 0) -> Any: ...

# From client
def handle_partition_stats(rpc: Any, dataset_id: Any, source_dataset_version: Any, target_dataset_version: Any, dataset_path: Any, skip_annotation_pipeline: Any) -> Any: ...

# From client
def handle_video_partition_stats(rpc: Any, dataset_id: Any, source_dataset_version: Any, target_dataset_version: Any, dataset_path: Any, skip_annotation_pipeline: Any, input_type: Any = 'youtube_bb') -> Any: ...

# From client
def start_client_processing_pipelines(rpc: Any, dataset_id: Any, dataset_version: Any, images_partition_status: Any, annotation_partition_status: Any, dataset_path: Any, is_annotations_compressed: Any, destination_bucket_alias: Any, account_number: Any, project_id: Any = None) -> Any: ...

# From client
def start_client_video_processing_pipelines(project_id: Any, rpc: Any, dataset_id: Any, dataset_version: Any, images_partition_status: Any, annotation_partition_status: Any, dataset_path: Any, is_annotations_compressed: Any, destination_bucket_alias: Any, account_number: Any, input_type: Any, num_dataset_items: Any) -> Any: ...

# From client
def upload_batch_files(batch: Any, max_attempts: Any = 5) -> Any: ...

# From client
def upload_video_batch_files(batch: Any, max_attempts: Any = 5) -> Any: ...

# From client
def upload_video_imagenet_batch_files(batch: Any, max_attempts: Any = 5) -> Any: ...

# From client
def upload_video_mot_batch_files(batch: Any, max_attempts: Any = 5) -> Any: ...

# From client_utils
def complete_dataset_items_upload(rpc: Any, dataset_id: Any, partition_stats: Any, target_version: Any = 'v1.0', source_version: Any = '', action_type: Any = 'data_import') -> Any: ...

# From client_utils
def compress_annotation_files(file_paths: Any, base_dataset_path: Any) -> Any: ...

# From client_utils
def create_partition_stats(rpc: Any, partition_stats: Any, dataset_id: Any, target_version: Any, source_version: Any = '') -> Any: ...

# From client_utils
def create_video_blank_dataset_items(partition_number: Any, rpc: Any, dataset_id: Any, dataset_version: Any, num_dataset_items: Any, project_id: Any) -> Any: ...

# From client_utils
def extract_frames_from_videos(file_paths: Any) -> Any: ...

# From client_utils
def get_annotations_partition(annotation_files: Any) -> Any: ...

# From client_utils
def get_batch_pre_signed_upload_urls(cloud_file_paths: Any, rpc: Any, type: Any, bucket_alias: Any = '', account_number: Any = '', project_id: Any = '') -> Any: ...

# From client_utils
def get_cloud_file_path(dataset_id: Any, dataset_version: Any, base_dataset_path: Any, file_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client_utils
def get_davis_partitions(video_files: Any) -> Any: ...

# From client_utils
def get_davis_relative_path(abs_path: str) -> str: ...
    """
    Extract the relative path starting from the grand-grandparent directory.
    
    Args:
        abs_path (str): Absolute path to the file
    
    Returns:
        str: Relative path starting from the grand-grandparent directory
    """

# From client_utils
def get_images_partitions(image_files: Any) -> Any: ...
    """
    Split image files into partitions and return partition stats.
    """

# From client_utils
def get_kinetics_partitions(video_files: Any) -> Any: ...

# From client_utils
def get_mot_partitions(video_files: Any) -> Any: ...

# From client_utils
def get_size_mb(path: Any) -> Any: ...
    """
    Calculate total size in MB for a file, folder, or list of paths.
    """

# From client_utils
def get_video_imagenet_partitions(video_files: Any) -> Any: ...

# From client_utils
def get_video_mot_cloud_file_path(dataset_id: Any, dataset_version: Any, base_dataset_path: Any, file_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client_utils
def get_video_mscoco_cloud_file_path(dataset_id: Any, dataset_version: Any, base_dataset_path: Any, file_path: Any, include_version_in_cloud_path: Any = False) -> Any: ...

# From client_utils
def get_video_mscoco_partitions(video_files: Any) -> Any: ...

# From client_utils
def get_youtube_bb_partitions(video_files: Any) -> Any: ...

# From client_utils
def get_youtube_bb_relative_path(abs_path: Any) -> Any: ...
    """
    Extract the relative path starting from the folder containing train/test/val directories.
    
    Args:
        abs_path (str): Absolute path to the file
    
    Returns:
        str: Relative path starting from the folder containing the parent directory of
            train/test/val
    """

# From client_utils
def is_file_compressed(file_path: Any) -> Any: ...

# From client_utils
def rename_davis_file(file_path: str) -> str: ...

# From client_utils
def rename_mot_file(file_path: str) -> str: ...

# From client_utils
def restructure_davis_dataset(base_path: Any) -> Any: ...
    """
    Restructure the DAVIS dataset to organize frames into segments and distribute them across train/test/val splits.
    All categories will be present in all splits, with segments of frames distributed across splits.
    
    Args:
        base_path (str): Path to the root of the DAVIS dataset
    """

# From client_utils
def scan_dataset(base_path: Any, rename_annotation_files: Any = False, input_type: Any = None) -> Any: ...

# From client_utils
def scan_folder(folder_path: Any) -> Any: ...

# From client_utils
def update_annotation_bucket_url(rpc: Any, dataset_id: Any, partition_number: Any, annotation_bucket_url: Any) -> Any: ...

# From client_utils
def update_partitions_numbers(rpc: Any, dataset_id: Any, items: Any, partition_key: Any = 'partitionNum') -> Any: ...

# From client_utils
def upload_compressed_dataset(rpc: Any, dataset_path: Any, bucket_alias: Any = '', account_number: Any = '', project_id: Any = '') -> Any: ...

# From client_utils
def upload_file(local_path: Any, presigned_url: Any, max_attempts: Any = 5) -> Any: ...

# From create_dataset
def create_dataset(session: Any, project_id: Any, account_number: Any, dataset_name: Any, project_type: Any = 'detection', dataset_type: Any = 'detection', input_type: Any = 'MSCOCO', dataset_path: Any = '', source_url: Any = '', url_type: Any = '', bucket_alias: Any = '', compute_alias: Any = '', target_cloud_storage: Any = '', source_credential_alias: Any = '', bucket_alias_service_provider: Any = 'auto') -> Any: ...
    """
    Create a new dataset.
    
    Parameters
    ----------
    session : Session
        The session object used for API interactions.
    project_id : str
        The ID of the project.
    account_number : str
        The account number associated with the session.
    project_type : str
        The type of project.
    dataset_name : str
        The name of the dataset.
    dataset_type : str, optional
        The type of dataset (default is "detection")
    input_type : str, optional
        The input type for the dataset (default is "MSCOCO")
    dataset_path : str, optional
        Local path to dataset files (default is "")
    source_url : str, optional
        URL to dataset source (default is "")
    url_type : str, optional
        Type of URL source (default is "")
    bucket_alias : str, optional
        Alias for cloud storage bucket (default is "")
    compute_alias : str, optional
        Alias for compute resources (default is "")
    target_cloud_storage : str, optional
        Target cloud storage location (default is "")
    source_credential_alias : str, optional
        Alias for source credentials (default is "")
    bucket_alias_service_provider : str, optional
        Service provider for bucket alias (default is "auto")
    
    Returns
    -------
    Dataset
        A Dataset object for the created dataset.
    
    Example
    -------
    >>> dataset = project._create_dataset(
    ...     dataset_name="MyDataset",
    ...     dataset_path="/path/to/data",
    ...     dataset_type="detection"
    ... )
    >>> print(f"Dataset created: {dataset}")
    """

# From data_augmentation
def augment_dataset_items(batch_dataset_items: Any, augmentation_fns: Any) -> Any: ...

# From data_augmentation
def batch_insert_dataset_items(batch: Any, dataset_id: Any, rpc: Any) -> Any: ...

# From data_augmentation
def calculate_partition_stats(dataset_items: List[Dict]) -> List[Dict]: ...
    """
    Calculate partition statistics for dataset items.
    
        Args:
            dataset_items: List of dataset items
    """

# From data_augmentation
def create_augmentation_fns(augmentation_configs: Dict) -> List[callable]: ...
    """
    Create a function to perform data augmentation.
    
        Args:
            augmentation_configs: Dictionary containing augmentation parameters
    
        Returns:
            List of augmentation functions
    """

# From data_augmentation
def download_images(dataset_items: List[Dict]) -> List[Dict]: ...
    """
    Download images for dataset items.
    
        Args:
            dataset_items: List of dataset items containing file locations and names
    
        Returns:
            List of successfully downloaded items
    """

# From data_augmentation
def filter_dataset_items(batch_dataset_items: Dict[str, List], dataset_version: str = 'v1.0') -> List[Dict]: ...
    """
    Filter dataset items based on the set type (train/test/val).
    
        Args:
            dataset_items: Dictionary containing version info and items
            dataset_version: Version string to filter by
    
        Returns:
            List of training items for the specified version
    """

# From data_augmentation
def get_data_augmentation_pipeline(rpc: Any, dataset_id: str, dataset_version: str, augmentation_configs: list, max_attempts: int = 5, bucket_alias: str = '', account_number: str = '') -> Any: ...
    """
    Get the data augmentation pipeline.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: Dataset ID
            dataset_version: Dataset version
            augmentation_configs: List of augmentation configurations
            max_attempts: Maximum number of upload retry attempts
            bucket_alias: Storage bucket alias
            account_number: Account number for storage access
    
        Returns:
            Configured Pipeline object for data augmentation
    """

# From data_augmentation
def load_bboxes(dataset_item: Any) -> Any: ...

# From data_augmentation
def load_image(dataset_item: Any) -> Any: ...

# From data_augmentation
def save_augmented_images(batch_dataset_items: Any, dataset_id: Any) -> Any: ...

# From data_augmentor
def create_completion_api_config() -> str: ...
    """
    Create completion API URL configuration
    """

# From data_augmentor
def create_kafka_config() -> Dict[str, Any]: ...
    """
    Create Kafka configuration with hardcoded values
    """

# From data_augmentor
def create_sample_pipeline_config() -> Dict[str, Any]: ...
    """
    Create a sample pipeline configuration for testing
    """

# From data_augmentor
def initialize_and_run_pipeline() -> Any: ...
    """
    Initialize and run the probability-based augmentation pipeline
    """

# From data_augmentor
def run_with_custom_config(config_file_path: str = None) -> Any: ...
    """
    Run pipeline with custom configuration from file
    """

# From data_augmentor
def transform_augmentation_data(input_dict: Any) -> Any: ...
    """
    Transform input augmentation dictionary into a list of output dictionaries,
    one for each augmentation chain.
    """

# From data_labelling
def add_dataset_item_annotations(dataset_item: Dict, prediction_result: Dict, project_type: str) -> Dict: ...
    """
    Add annotations to dataset item based on prediction results
    
        Args:
            dataset_item: Dataset item to annotate
            prediction_result: Prediction results
            project_type: Type of project (classification/detection/instance_segmentation)
    
        Returns:
            Dict: Annotated dataset item
    
        Raises:
            Exception: If annotation fails
    """

# From data_labelling
def convert_to_mscoco_format(x_min: float, y_min: float, x_max: float, y_max: float) -> List[float]: ...
    """
    Convert bounding box coordinates to MSCOCO format.
    
        Args:
            x_min: Minimum x coordinate
            y_min: Minimum y coordinate
            x_max: Maximum x coordinate
            y_max: Maximum y coordinate
    
        Returns:
            List[float]: [x_min, y_min, width, height]
    """

# From data_labelling
def create_model_deployment_client(session: Any, project_type: str, project_id: str, model_id: str = '', model_type: str = 'pretrained', deployment_type: str = 'regular', checkpoint_type: str = 'pretrained', checkpoint_value: str = '', suggested_classes: List[str] = [], compute_alias: str = '', runtime_framework: str = 'Pytorch', model_family: str = '', model_key: str = '') -> Union[MatriceDeployClient, Deployment]: ...
    """
    Create and test a model deployment
    
        Args:
            session: Session object
            project_type: Type of project
            project_id: ID of project
            model_id: ID of model
            model_type: Type of model
            deployment_type: Type of deployment
            checkpoint_type: Type of checkpoint
            checkpoint_value: Value of checkpoint
            suggested_classes: List of suggested classes
            compute_alias: Compute alias
            runtime_framework: Runtime framework
            model_family: Model family name
            model_key: Model key identifier
    
        Returns:
            MatriceDeployClient: Deployment client if successful
    
        Raises:
            Exception: If deployment fails
    """

# From data_labelling
def get_dataset_labelling_pipeline(session: Any, dataset_id: str, dataset_version: str, deploy_client: Any, project_type: str) -> Any: ...
    """
    Create dataset labeling pipeline
    
        Args:
            session: Session object
            dataset_id: ID of dataset
            dataset_version: Version of dataset
            deploy_client: Deployment client for predictions
            project_type: Type of project
    
        Returns:
            Pipeline: Configured pipeline object
    
        Raises:
            Exception: If pipeline creation fails
    """

# From data_labelling
def label_dataset_items(batch_dataset_items: List[Dict], deploy_client: Union[MatriceDeployClient, Deployment], project_type: str, dataset_version: str) -> List[Dict]: ...
    """
    Label batch of dataset items using model predictions
    
        Args:
            batch_dataset_items: List of dataset items to label
            deploy_client: Deployment client
            project_type: Type of project
            dataset_version: Version of dataset
    
        Returns:
            List[Dict]: Labeled dataset items
    
        Raises:
            Exception: If labeling fails
    """

# From data_labelling
def test_model_prediction(session: Any, deployment_class: Any, max_tries: int = 5, initial_wait: int = 180, retry_wait: int = 180) -> Union[MatriceDeployClient, Deployment]: ...
    """
    Test model prediction with retries
    
        Args:
            session: Session object
            deployment_class: Model deployment object
            max_tries: Maximum number of prediction attempts
            initial_wait: Initial wait time in seconds
            retry_wait: Wait time between retries in seconds
    
        Returns:
            Optional[MatriceDeployClient]: Deploy client if successful, None otherwise
    """

# From data_labelling
def update_dataset_items_keys(dataset_items: List[Dict], dataset_version: str) -> List[Dict]: ...
    """
    Update dataset items keys
    
        Args:
            dataset_items: List of dataset items
            dataset_version: Version of dataset
    
        Returns:
            List[Dict]: Updated dataset items
    """

# From data_prep
def check_image_validity(local_filename: str, frame_num: int) -> Optional[str]: ...
    """
    Helper function to validate downloaded image files.
    
    Args:
        local_filename: Path to the downloaded file
        frame_num: Frame number for logging
    
    Returns:
        Local filename if valid, None otherwise
    """

# From data_prep
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

# From data_prep
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

# From data_prep
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

# From data_prep
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

# From data_prep
def download_davis_yolo_frames(dataset_item: Dict, base_dataset_path: str, dataset_version: str, frame_split_map: Optional[Dict[Tuple[str, str], str]] = None) -> None: ...

# From data_prep
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

# From data_prep
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

# From data_prep
def download_segment_videos(dataset_items: List[Dict], input_format: str, base_dataset_path: str, dataset_version: str) -> List[Dict]: ...

# From data_prep
def extract_video_name_from_url(url: str) -> str: ...
    """
    Extracts video name from the frame's URL path.
    """

# From data_prep
def get_categories_id_map(dataset_items: List[Dict], start_id: int = 0) -> Dict[str, int]: ...
    """
    Get mapping of categories to IDs.
    
        Args:
            dataset_items: List of dataset items
            start_id: Starting ID for categories
    
        Returns:
            Dictionary mapping category names to IDs
    """

# From data_prep
def get_category_name(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get category name from dataset item annotations.
    """

# From data_prep
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

# From data_prep
def get_image_annotations(dataset_item: Dict, dataset_version: str = 'v1.0') -> List[Dict]: ...
    """
    Get annotations for a dataset item.
    """

# From data_prep
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

# From data_prep
def get_item_set_type(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get the set type (train/test/val) for a dataset item.
    """

# From data_prep
def get_kinetics_annotations(dataset_item: Dict, dataset_version: str = 'v1.0') -> List[Dict]: ...
    """
    Get annotations for a dataset item.
    """

# From data_prep
def get_kinetics_category_name(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get category name from dataset item annotations.
    """

# From data_prep
def get_mscoco_annotations(dataset_items: List[Dict], categories_id_map: Dict[str, int]) -> List[Dict]: ...
    """
    Extract MSCOCO annotations from dataset items.
    
        Args:
            dataset_items: List of dataset items
            categories_id_map: Dictionary mapping categories to IDs
    
        Returns:
            List of annotation dictionaries in MSCOCO format
    """

# From data_prep
def get_mscoco_categories(categories_id_map: Dict[str, int]) -> List[Dict]: ...
    """
    Extract MSCOCO categories from dataset items.
    
        Args:
            categories_id_map: Dictionary mapping categories to IDs
    
        Returns:
            List of category dictionaries in MSCOCO format
    """

# From data_prep
def get_mscoco_images(dataset_items: List[Dict]) -> List[Dict]: ...
    """
    Extract MSCOCO images from dataset items.
    
        Args:
            dataset_items: List of dataset items
    
        Returns:
            List of image dictionaries in MSCOCO format
    """

# From data_prep
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

# From data_prep
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

# From data_prep
def get_video_item_set_type(dataset_item: Dict, dataset_version: str = 'v1.0') -> str: ...
    """
    Get the set type (train/test/val) for a dataset item.
    """

# From data_prep
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

# From data_prep
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

# From data_prep
def process_final_annotations(dataset_items: List[List[Dict]], base_dataset_path: str, input_format: str, dataset_version: str) -> None: ...
    """
    Process final annotations after pipeline completion.
    
        Args:
            dataset_items: List of dataset items to process
            base_dataset_path: Base path to save dataset files
            input_format: Format of annotations (YOLO/COCO)
            dataset_version: Dataset version
    """

# From data_prep
def segment_and_split_by_category(dataset_items: List[Dict], n_frames_per_segment: int = 2, split_ratios: Tuple[float, float, float] = (0.8, 0.1, 0.1), seed: int = 42) -> Dict[str, str]: ...
    """
    Returns a mapping of frame IDs (video_id + frame_id) to split types.
    Groups frames category-wise into segments of n frames,
    then splits them into train/val/test.
    """

# From data_prep
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

# From data_prep
def write_data_yaml(categories_id_map: Dict[str, int], yaml_file_path: str) -> None: ...
    """
    Write category data to YAML file.
    
        Args:
            categories_id_map: Dictionary mapping categories to IDs
            yaml_file_path: Path to save YAML file
    """

# From data_prep
def write_davis_yolo_annotations(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...

# From data_prep
def write_kinetics_labels(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
    """
    Write Kinetics format labels (CSV) for videos.
    
    Args:
        local_path: Base path to save annotations.
        dataset_items: List of dataset items (videos).
        dataset_version: Dataset version (e.g., v1.0).
    """

# From data_prep
def write_mscoco_annotation_file(dataset_items: List[Dict], categories_id_map: Dict[str, int], ann_json_path: str) -> None: ...
    """
    Write MSCOCO annotation file in COCO format.
    
        Args:
            dataset_items: List of dataset items
            categories_id_map: Dictionary mapping categories to IDs
            ann_json_path: Path to save annotation file
    """

# From data_prep
def write_mscoco_annotation_files(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
    """
    Write MSCOCO annotation files for different itemSetTypes.
    
        Args:
            local_path: Base path to save annotation files
            dataset_items: List of dataset items
            dataset_version: Dataset version
    """

# From data_prep
def write_video_coco_annotations(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...

# From data_prep
def write_yolo_labels(local_path: str, dataset_items: List[Dict], dataset_version: str) -> None: ...
    """
    Write YOLO format labels for images.
    
        Args:
            local_path: Base path to save labels
            dataset_items: List of dataset items
            dataset_version: Dataset version
    """

# From image_augmentations
def get_augmentation_compose(augmentation_config: Dict[str, Dict[str, Any]]) -> Any: ...

# From image_data_augmentation
def apply_augmentations_stage(dataset_item: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...

# From image_data_augmentation
def completion_monitor_stage(dataset_item: Any, probability_manager: Any, pipeline_config: Any, **kwargs: Any) -> Any: ...

# From image_data_augmentation
def create_probability_based_augmentation_pipeline(pipeline_config: Any, kafka_config: Dict[str, Any]) -> Optional[Pipeline]: ...

# From image_data_augmentation
def download_images_stage(dataset_item: Any, upload_url_manager: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...

# From image_data_augmentation
def fetch_dataset_items_stage(dataset_item: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...

# From image_data_augmentation
def fetch_upload_urls_stage(dataset_item: Any, pipeline_config: Any, upload_url_manager: Any, probability_manager: Any, **kwargs: Any) -> Any: ...

# From image_data_augmentation
def get_kafka_brokers() -> Any: ...

# From image_data_augmentation
def get_object_key_from_url(source_url: str) -> str: ...

# From image_data_augmentation
def parse_dynamic_pipeline_config(config_data: Dict, source_dataset_version: str = 'v1.0', target_dataset_version: str = 'v1.1') -> Any: ...
    """
    Parse dynamic pipeline configuration from input data
    """

# From image_data_augmentation
def upload_and_publish_stage(dataset_item: Any, new_items_producer: Any, new_items_topic: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...

# From new_data_augmentation
def apply_augmentations_stage(augmentation_queue: Any, update_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 3: Apply augmentations to images
    """

# From new_data_augmentation
def create_data_augmentation_pipeline(kafka_config: Dict[str, Any]) -> Optional[Pipeline]: ...
    """
    Create and configure the data augmentation pipeline
    
    Args:
        kafka_config: Configuration for Kafka consumer/producer
    
    Returns:
        Configured Pipeline instance
    """

# From new_data_augmentation
def download_images_stage(download_queue: Any, augmentation_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 2: Download images from S3 URLs
    """

# From new_data_augmentation
def fetch_dataset_items_stage(dataset_items_queue: Any, download_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 1: Fetch dataset items from input queue
    This is essentially a pass-through stage that can add any preprocessing if needed
    """

# From new_data_augmentation
def kafka_consumer_producer(consumer_topic: str, producer_topic: str, bootstrap_servers: List[str], dataset_items_queue: Any, output_queue: Any, consumer_group: str = 'augmentation_pipeline') -> Any: ...
    """
    Kafka consumer to populate input queue and producer to publish output
    """

# From new_data_augmentation
def update_and_upload_stage(update_queue: Any, output_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 4: Update dataset item metadata and upload augmented image to S3
    """

# From server
def batch_calculate_sample_properties(batch_sample_details: List[Dict[str, Any]], properties_calculation_fn: Any) -> List[Dict[str, Any]]: ...
    """
    Calculate properties for a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
    
        Returns:
            List of processed image details
    """

# From server
def batch_download_samples(batch_image_details: List[Dict[str, Any]], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> List[Dict[str, Any]]: ...
    """
    Download a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
            rpc: RPC client for making API calls
    
        Returns:
            List of updated sample details
    """

# From server
def batch_download_video_samples(batch_image_details: List[Dict[str, Any]], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> List[Dict[str, Any]]: ...
    """
    Download a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
            rpc: RPC client for making API calls
    
        Returns:
            List of updated sample details
    """

# From server
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

# From server
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

# From server
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

# From server
def batch_update_video_davis_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, project_id: str, attempts: int = 3, batch_segment_limit: int = 10, frames_per_segment: int = 16) -> List[Dict[str, Any]]: ...
    """
    Update high-level video info and segment-wise annotations for DAVIS-style datasets.
    """

# From server
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

# From server
def batch_update_video_mot_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, project_id: str, attempts: int = 3, segments_per_request: int = 10) -> List[Dict[str, Any]]: ...

# From server
def batch_update_video_mscoco_dataset_items(batch_image_details: List[Dict[str, Any]], rpc: Any, dataset_id: str, version: str, project_id: str, attempts: int = 3, frames_per_segment: int = 16, batch_segment_limit: int = 10) -> List[Dict[str, Any]]: ...
    """
    Update video metadata and segment-wise annotations in MSCOCO to match DAVIS format.
    """

# From server
def batch_upload_video_samples(batch_image_details: List[Dict[str, Any]], rpc: Any, bucket_alias: str = '', account_number: str = '') -> List[Dict[str, Any]]: ...
    """
    Download a batch of samples.
    
        Args:
            batch_image_details: List of image details dictionaries
            rpc: RPC client for making API calls
    
        Returns:
            List of updated sample details
    """

# From server
def calculate_image_properties(image_details: Dict[str, Any]) -> Dict[str, Any]: ...
    """
    Calculate properties of an image.
    
        Args:
            image_details: Dictionary containing image metadata
    
        Returns:
            Updated image details with calculated properties
    """

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server
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

# From server_utils
def chunk_items(items: List[Dict[str, Any]], chunk_size: int) -> List[List[Dict[str, Any]]]: ...
    """
    Chunk items into smaller batches.
    
    Args:
        items: List of items to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunked item batches
    """

# From server_utils
def construct_relative_path(dataset_id: str, folder_name: str, file_name: str) -> str: ...
    """
    Construct relative path from components.
    
    Args:
        dataset_id: Dataset identifier
        folder_name: Name of folder
        file_name: Name of file
    
    Returns:
        Constructed relative path
    """

# From server_utils
def delete_tmp_folder(tmp_folder_path: str) -> None: ...
    """
    Delete temporary folder.
    
    Args:
        tmp_folder_path: Path to temporary folder
    """

# From server_utils
def download_file(url: str, file_path: str, timeout: int = 60, chunk_size: int = 8192, max_retries: int = 1) -> str: ...
    """
    Download file from URL to specified path with improved reliability.
    
    Args:
        url: URL to download from
        file_path: Path to save file to
        timeout: Request timeout in seconds
        chunk_size: Size of chunks to download
    
    Returns:
        Path where file was saved
    
    Raises:
        Exception: If download fails
    """

# From server_utils
def enrich_items_with_file_info(rpc: Any, items: List[Dict[str, Any]], download_images_required: bool = False) -> List[Dict[str, Any]]: ...
    """
    Enriches dataset items with file and annotation information, including presigned URLs if requested.
    
    Args:
        rpc: RPC client for making API calls
        items: List of dataset items to enrich
        download_images_required: Whether to get presigned URLs for images
    
    Returns:
        List of enriched dataset items
    """

# From server_utils
def extract_dataset(dataset_path: str, get_inner_dir: bool = False) -> str: ...
    """
    Extract compressed dataset.
    
    Args:
        dataset_path: Path to compressed dataset
        get_inner_dir: Whether to return inner directory path
    
    Returns:
        Path to extracted dataset
    
    Raises:
        ValueError: If archive format is unsupported
        Exception: If extraction fails
    """

# From server_utils
def extract_davis_video_name(file_path: str) -> str: ...

# From server_utils
def fetch_all_annotations(rpc: Any, dataset_item_id: str, version: str) -> List[Dict[str, Any]]: ...

# From server_utils
def fetch_all_file_info(rpc: Any, dataset_item_id: str) -> List[Dict[str, Any]]: ...

# From server_utils
def fetch_annotation_info(rpc: Any, dataset_item_id: str, version: str, page_size: int = 10) -> List[Dict[str, Any]]: ...
    """
    Fetches all annotation information for a specific dataset item and version across pages.
    
    Args:
        rpc: RPC client for making API calls
        dataset_item_id: Dataset item identifier
        version: Version identifier
        page_size: Number of items per page
    
    Returns:
        A list of all annotation information items
    """

# From server_utils
def fetch_base_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, page_size: int) -> List[Dict[str, Any]]: ...

# From server_utils
def fetch_data_prep_video_frame_items(rpc: Any, path: str, request_batch_size: int, page_number: Optional[int] = None, download_images_required: bool = True, is_file_info_required: bool = True, isAnnotationInfoRequired: bool = True) -> List[Dict[str, Any]]: ...
    """
    Fetch video frame items from the dataset API.
    
    Args:
        rpc: RPC client for making API calls
        path: API path to fetch items
        request_batch_size: Number of items to fetch per page
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs for images
        is_file_info_required: Whether file info is required
    
    Returns:
        List of dataset items
    """

# From server_utils
def fetch_file_info(rpc: Any, dataset_item_id: str, download_images_required: bool = False, page_size: int = 10) -> List[Dict[str, Any]]: ...
    """
    Fetches all file information for a specific dataset item across pages.
    
    Args:
        rpc: RPC client for making API calls
        dataset_item_id: Dataset item identifier
        download_images_required: Whether to get presigned URLs
        page_size: Number of items per page
    
    Returns:
        A list of all file information items
    """

# From server_utils
def fetch_items(rpc: Any, path: str, request_batch_size: int, page_number: Optional[int] = None, download_images_required: bool = False) -> List[Dict[str, Any]]: ...
    """
    Fetch items from the dataset API.
    
    Args:
        rpc: RPC client for making API calls
        path: API path to fetch items
        request_batch_size: Number of items to fetch per page
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs for images
    
    Returns:
        List of dataset items
    """

# From server_utils
def fetch_video_frame_items(rpc: Any, path: str, request_batch_size: int, page_number: Optional[int] = None, download_images_required: bool = False, is_file_info_required: bool = False) -> List[Dict[str, Any]]: ...
    """
    Fetch video frame items from the dataset API.
    
    Args:
        rpc: RPC client for making API calls
        path: API path to fetch items
        request_batch_size: Number of items to fetch per page
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs for images
        is_file_info_required: Whether file info is required
    
    Returns:
        List of dataset items
    """

# From server_utils
def generate_short_uuid() -> str: ...
    """
    Generate a shortened UUID.
    
    Returns:
        Short UUID string
    """

# From server_utils
def get_batch_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get a batch of items from a specific dataset version page.
    """

# From server_utils
def get_batch_partition_items(rpc: Any, dataset_id: str, partition: int, page_number: int, download_images_required: bool = False, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get a batch of items from a specific partition page.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
    
    Returns:
        List of partition items
    """

# From server_utils
def get_batch_pre_signed_download_urls(cloud_file_paths: List[str], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> Dict: ...
    """
    Get batch of pre-signed download URLs.
    
    Args:
        cloud_file_paths: List of cloud file paths
        rpc: RPC client
        bucket_alias: Optional bucket alias
        account_number: Optional account number
    
    Returns:
        Response data or error message
    """

# From server_utils
def get_batch_video_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get a batch of items from a specific dataset version page.
    """

# From server_utils
def get_classwise_frame_splits(partition_items: List[Dict], annotation_type: str = 'detection', sample_stats: Optional[Dict] = None) -> Tuple[Dict, Dict]: ...
    """
    Get class-wise split statistics for video frames.
    
    Args:
        partition_items: List of partition items
        annotation_type: Type of annotation
        sample_stats: Optional sample statistics
    
    Returns:
        Tuple of class-wise split statistics and unique video statistics
    """

# From server_utils
def get_classwise_splits(partition_items: List[Dict], annotation_type: str = 'classification') -> Dict: ...
    """
    Get class-wise split statistics.
    
    Args:
        partition_items: List of partition items
        annotation_type: Type of annotation
    
    Returns:
        Dictionary of class-wise split statistics
    """

# From server_utils
def get_corresponding_split_type(path: str, include_year: bool = False) -> str: ...
    """
    Get the split type (train/val/test) from a file path.
    
    Args:
        path: File path to analyze
        include_year: Whether to include year in split type
    
    Returns:
        Split type string
    """

# From server_utils
def get_data_prep_batch_video_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, request_batch_size: int = 100, input_type: str = 'davis') -> List[Dict[str, Any]]: ...
    """
    Fetch dataset items and enrich with file info and annotation info.
    """

# From server_utils
def get_filename_from_url(url: str) -> str: ...
    """
    Extract filename from URL.
    
    Args:
        url: URL to parse
    
    Returns:
        Extracted filename
    """

# From server_utils
def get_number_of_dataset_batches(rpc: Any, dataset_id: str, dataset_version: str, request_batch_size: int = 1) -> int: ...
    """
    Calculate total number of pages for a dataset.
    """

# From server_utils
def get_number_of_partition_batches(rpc: Any, dataset_id: str, partition: int, request_batch_size: int = 1) -> int: ...
    """
    Calculate total number of pages for a partition.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        request_batch_size: Number of items per batch
    
    Returns:
        Number of pages
    """

# From server_utils
def get_partition_items(rpc: Any, dataset_id: str, partition: int, download_images_required: bool = False, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get all items for a partition.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
    
    Returns:
        List of all partition items
    """

# From server_utils
def get_unprocessed_partitions(rpc: Any, dataset_id: str, version: str) -> List[int]: ...
    """
    Get list of unprocessed partition numbers.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        version: Dataset version
    
    Returns:
        List of unprocessed partition numbers
    """

# From server_utils
def get_video_frame_batch_partition_items(rpc: Any, dataset_id: str, partition: int, page_number: int, download_images_required: bool = False, request_batch_size: int = 100, is_file_info_required: bool = False, input_type: str = 'mscoco_video') -> List[Dict[str, Any]]: ...
    """
    Get a batch of video frame items from a specific partition page.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
        is_file_info_required: Whether file info is required
    
    Returns:
        List of partition items with added file info and presigned URLs if requested
    """

# From server_utils
def get_video_frame_partition_items(rpc: Any, dataset_id: str, partition: int, download_images_required: bool = False, request_batch_size: int = 100, is_file_info_required: bool = True, input_type: str = 'mscoco_video') -> List[Dict[str, Any]]: ...
    """
    Get all video frame items for a partition.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
        is_file_info_required: Whether file info is required
    
    Returns:
        List of all partition items
    """

# From server_utils
def handle_source_url_dataset_download(source_url: Any) -> str: ...
    """
    Handle dataset download from source URL.
    """

# From server_utils
def log_error(action_record_id: str, exception: Any, filename: str, function_name: str, rpc: Any) -> None: ...
    """
    Log error to system.
    
    Args:
        action_record_id: Action record identifier
        exception: Exception that occurred
        filename: Name of file where error occurred
        function_name: Name of function where error occurred
        rpc: RPC client
    """

# From server_utils
def paginate_all(rpc: Any, path_template: str) -> List[Dict[str, Any]]: ...

# From server_utils
def rpc_get_call(rpc: Any, path: str, params: Optional[Dict] = None) -> Optional[Dict]: ...
    """
    Make RPC GET call.
    
    Args:
        rpc: RPC client
        path: API path
        params: Optional query parameters
    
    Returns:
        Response data or None on failure
    """

# From server_utils
def update_action_status(action_record_id: str, action_type: str, step_code: str, status: str, status_description: str, rpc: Any) -> None: ...
    """
    Update action status.
    
    Args:
        action_record_id: Action record identifier
        action_type: Type of action
        step_code: Code for current step
        status: Status to set
        status_description: Description of status
        rpc: RPC client
    """

# From server_utils
def update_partition_status(rpc: Any, action_record_id: str, dataset_id: str, version: str, partition: int, status: str, partition_items: List[Dict], annotation_type: str) -> Optional[Dict]: ...
    """
    Update partition processing status.
    
    Args:
        rpc: RPC client
        action_record_id: Action record identifier
        dataset_id: Dataset identifier
        version: Dataset version
        partition: Partition number
        status: Status to set
        partition_items: Items in partition
        annotation_type: Type of annotation
    
    Returns:
        Response data or None on failure
    
    Raises:
        Exception: If update fails
    """

# From server_utils
def update_video_frame_partition_status(rpc: Any, action_record_id: str, dataset_id: str, version: str, partition: int, status: str, partition_items: List[Dict], annotation_type: str, sample_stats: Optional[Dict] = None) -> Optional[Dict]: ...
    """
    Update video frame partition processing status.
    
    Args:
        rpc: RPC client
        action_record_id: Action record identifier
        dataset_id: Dataset identifier
        version: Dataset version
        partition: Partition number
        status: Status to set
        partition_items: Items in partition
        annotation_type: Type of annotation
        sample_stats: Optional sample statistics
    
    Returns:
        Response data or None on failure
    
    Raises:
        Exception: If update fails
    """

# From video_server
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

# From video_server
def calculate_video_properties(video_details: Dict[str, Any]) -> Dict[str, Any]: ...
    """
    Calculate properties of a video.
    
        Args:
            video_details: Dictionary containing video metadata
    
        Returns:
            Updated video details with calculated properties
    """

# From video_server
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

# Classes
# From aug_server
class AugmentationRequest(BaseModel):
    """
    Request model for augmentation endpoint.
    """

    pass

# From aug_server
class AugmentationResponse(BaseModel):
    """
    Response model for augmentation endpoint.
    """

    pass

# From aug_server
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


# From aug_server_v2
class AugmentationRequest(BaseModel):
    """
    Request model for augmentation endpoint.
    """

    pass

# From aug_server_v2
class AugmentationResponse(BaseModel):
    """
    Response model for augmentation endpoint.
    """

    pass

# From aug_server_v2
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


# From aug_server_v2
class AugmentationStep:
    """
    Represents a single augmentation step.
    """

    pass

# From aug_server_v2
class AugmentationStrategyFactory:
    """
    Factory class to create augmentation strategy instances.
    """

    STRATEGIES: Dict[Any, Any]

    def create_strategy(cls: Any, aug_step: Any) -> Any: ...


# From aug_server_v2
class ImageAugmentationStrategy(ABC):
    def __init__(self: Any, **kwargs: Any) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Any: ...


# From data_augmentation
class DataAugmentation:
    """
    Class to handle dataset preparation.
    """

    def __init__(self: Any, session: Any, action_record_id: str) -> None: ...
        """
        Initialize DataAugmentation.
        
                Args:
                    session: Session object with RPC client
                    action_record_id: ID of action record
        """

    def start_processing(self: Any) -> None: ...
        """
        Start dataset augmentation processing.
        """

    def update_status(self: Any, stepCode: str, status: str, status_description: str) -> None: ...
        """
        Update status of data preparation.
        
                Args:
                    stepCode: Code indicating current step
                    status: Status of step
                    status_description: Description of status
        """


# From data_augmentor
class DataAugmentation:
    """
    Class to handle dataset preparation.
    """

    def __init__(self: Any, session: Any, action_record_id: str) -> None: ...
        """
        Initialize DataAugmentation.
        
                Args:
                    session: Session object with RPC client
                    action_record_id: ID of action record
        """

    def start_processing(self: Any) -> None: ...
        """
        Start dataset augmentation processing.
        """

    def update_status(self: Any, stepCode: str, status: str, status_description: str) -> None: ...
        """
        Update status of data preparation.
        
                Args:
                    stepCode: Code indicating current step
                    status: Status of step
                    status_description: Description of status
        """


# From data_labelling
class DataLabelling:
    """
    Class to handle dataset labelling.
    """

    def __init__(self: Any, session: Any, action_record_id: str) -> None: ...
        """
        Initialize DataLabelling.
        
                Args:
                    session: Session object with RPC client
                    action_record_id: ID of action record
        
                Raises:
                    Exception: If initialization fails
        """

    def create_model_deployment(self: Any) -> Any: ...
        """
        Create model deployment
        
                Returns:
                    MatriceDeployClient: Deployment client
        
                Raises:
                    Exception: If deployment creation fails
        """

    def mark_dataset_as_labelled(self: Any) -> None: ...
        """
        Mark dataset as labelled
        
                Raises:
                    Exception: If marking dataset as labelled fails
        """

    def start_processing(self: Any) -> None: ...
        """
        Start dataset labelling processing.
        
                Raises:
                    Exception: If processing fails
        """

    def update_status(self: Any, stepCode: str, status: str, status_description: str, sample_count: int = None) -> None: ...
        """
        Update status of data labelling.
        
                Args:
                    stepCode: Code indicating current step
                    status: Status of step
                    status_description: Description of status
        
                Raises:
                    Exception: If status update fails
        """


# From data_prep
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


# From data_processor
class DataProcessor:
    """
    Class for processing data through various pipelines.
    """

    def __init__(self: Any, session: Any, action_record_id: Any) -> None: ...
        """
        Initialize DataProcessor with session and action record ID.
        """

    def get_server_processing_pipeline(self: Any) -> Any: ...
        """
        Get the appropriate server processing pipeline based on input type.
        """

    def start_processing(self: Any) -> Any: ...
        """
        Start the data processing pipeline.
        """

    def update_status(self: Any, step_code: Any, status: Any, status_description: Any, sample_count: Any = None) -> None: ...
        """
        Update the status of the data processing job.
        """


# From image_data_augmentation
class AugmentationStep:
    """
    Represents a single augmentation step
    """

    pass

# From image_data_augmentation
class AugmentationStrategyFactory:
    """
    Factory class to create augmentation strategy instances
    """

    STRATEGIES: Dict[Any, Any]

    def create_strategy(cls: Any, aug_step: Any) -> Any: ...


# From image_data_augmentation
class DynamicPipelineConfig:
    """
    Configuration for dynamic augmentation pipeline
    """

    pass

# From image_data_augmentation
class DynamicProbabilityDistributionManager:
    """
    Manages dynamic probability distribution for augmentations with global combination tracking
    """

    def __init__(self: Any, config: Any) -> None: ...

    NON_REPEATING_AUGS: Set[Any]

    def add_available_image(self: Any, image_id: str) -> Any: ...
        """
        Add an image ID to the pool of available images
        """

    def get_status(self: Any) -> Dict[str, Any]: ...
        """
        Get current status and statistics
        """

    def get_usage_distribution(self: Any) -> Dict[str, float]: ...
        """
        Get the distribution of augmentation usage as percentages
        """

    def increment_generated_count(self: Any) -> Any: ...
        """
        Increment the count of generated images
        """

    def is_complete(self: Any) -> bool: ...
        """
        Check if target number of images has been generated
        """

    def select_augmentations_for_image(self: Any, image_id: str) -> Optional[List[AugmentationStep]]: ...
        """
        Select a random combination of augmentations with combination coverage
        """


# From image_data_augmentation
class ImageAugmentationStrategy(ABC):
    """
    Base class for image augmentation strategies
    """

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...


# From image_data_augmentation
class ImageDataItem:
    """
    Represents an image dataset item with all necessary metadata
    """

    def __init__(self: Any, json_data: Dict) -> None: ...

    def create_augmented_copy(self: Any) -> Any: ...
        """
        Create a new ImageDataItem for the augmented version
        """

    def get_bboxes(self: Any, source_version: Any) -> List[List[float]]: ...
        """
        Extract bounding boxes from version info
        """

    def get_json_data(self: Any) -> Dict: ...
        """
        Get the updated JSON data
        """

    def update_bboxes(self: Any, new_bboxes: List[List[float]], source_version: str) -> Any: ...
        """
        Update bounding boxes in version info
        """

    def update_dimensions(self: Any, new_height: int, new_width: int) -> Any: ...
        """
        Update image dimensions
        """


# From image_data_augmentation
class PaginatedDataManager:
    """
    Manages paginated data requests and responses
    """

    def __init__(self: Any, request_topic: str, response_topic: str, bootstrap_servers: str, consumer_group: str = 'augmentation_pipeline_consumer', page_size: int = 100, max_retries: int = 3, retry_delay: int = 5) -> None: ...

    def check_for_responses(self: Any, expected_augmentation_id: str = None) -> List[ImageDataItem]: ...

    def is_pagination_complete(self: Any) -> bool: ...

    def request_page(self: Any, page_number: int, dataset_id: str = None, augmentation_id: str = None, source_version: str = 'v1.0', **kwargs: Any) -> bool: ...


# From image_data_augmentation
class UploadURLManager:
    """
    Manages upload URL requests and responses
    """

    def __init__(self: Any, request_topic: str, response_topic: str, bootstrap_servers: str, consumer_group: str = 'upload_url_consumer') -> None: ...

    def close(self: Any) -> Any: ...

    def get_upload_url(self: Any, timeout_seconds: int = 60, expected_augmentation_id: str = None) -> Optional[str]: ...

    def has_pending_requests(self: Any) -> bool: ...

    def request_upload_url(self: Any, dataset_id: str, augmentation_id: str = None) -> bool: ...


# From new_data_augmentation
class AugmentationStrategyFactory:
    """
    Factory class to create augmentation strategy instances
    """

    STRATEGIES: Dict[Any, Any]

    def create_strategy(cls: Any, aug_config: Dict) -> Any: ...
        """
        Create augmentation strategy from configuration
        """


# From new_data_augmentation
class DatasetItem:
    """
    Represents a dataset item with all necessary metadata
    """

    def __init__(self: Any, json_data: Dict) -> None: ...

    def get_json_data(self: Any) -> Dict: ...
        """
        Get the updated JSON data
        """

    def update_json_fields(self: Any, updated_fields: Dict) -> Any: ...
        """
        Update specific fields in the JSON data
        """


# From pipeline
class Pipeline:
    def __init__(self: Any) -> None: ...

    def add_producer(self: Any, process_fn: Any, process_params: Optional[Dict[str, Any]] = None, partition_num: int = 0) -> None: ...
        """
        Add a producer stage that generates data for the pipeline.
        """

    def add_stage(self: Any, stage_name: str, process_fn: Any, pull_queue: Optional[Queue] = None, push_queue: Optional[Queue] = None, process_params: Optional[Dict[str, Any]] = None, num_threads: int = 1, is_last_stage: bool = False) -> None: ...
        """
        Add a new processing stage to the pipeline.
        """

    def add_stop_callback(self: Any, callback: Any, process_params: Optional[Dict[str, Any]] = None) -> None: ...
        """
        Add a callback to execute when pipeline stops.
        """

    def call_stop_callbacks(self: Any) -> None: ...
        """
        Execute all registered stop callbacks.
        """

    def get_all_items_from_last_stage(self: Any) -> List[Any]: ...
        """
        Get all items from the last stage.
        """

    def manage_stages_sleep_and_wake_up(self: Any) -> None: ...
        """
        Manage stage execution by pausing/resuming based on partition progress.
        """

    def remove_stage(self: Any, stage_name: str) -> None: ...
        """
        Remove a stage from the pipeline.
        """

    def sleep_stage(self: Any, stage_name: str) -> None: ...
        """
        Pause a specific stage.
        """

    def start(self: Any) -> None: ...
        """
        Start all pipeline stages and management threads.
        """

    def start_producers(self: Any) -> None: ...
        """
        Start all producer threads in order of partition number.
        """

    def start_stage(self: Any, stage_name: str) -> None: ...
        """
        Start a specific stage.
        """

    def stop(self: Any) -> None: ...
        """
        Stop all pipeline stages and execute callbacks.
        """

    def wait_to_finish_processing_and_stop(self: Any) -> None: ...
        """
        Wait for all processing to complete and stop the pipeline.
        """


# From pipeline
class PipelineStage:
    def __init__(self: Any, stage_name: str, pull_queue: Optional[Queue], push_queue: Optional[Queue], process_fn: Any, process_params: Dict[str, Any], num_threads: int) -> None: ...
        """
        Initialize a pipeline stage.
        
                Args:
                    stage_name: Name of the stage
                    pull_queue: Queue to pull samples from
                    push_queue: Queue to push processed samples to
                    process_fn: Function to process samples
                    process_params: Parameters for the process function
                    num_threads: Number of worker threads
        """

    def join(self: Any) -> None: ...
        """
        Stop processing and wait for all workers to finish.
        """

    def sleep(self: Any) -> None: ...
        """
        Pause processing by setting sleep flag.
        """

    def start(self: Any) -> None: ...
        """
        Start processing samples by launching worker threads.
        """

    def stop(self: Any) -> None: ...
        """
        Stop processing by setting stop flag.
        """

    def wake_up(self: Any) -> None: ...
        """
        Resume processing by clearing sleep flag.
        """


from . import aug_server, aug_server_v2, client, client_utils, create_dataset, data_augmentation, data_augmentor, data_labelling, data_prep, data_processor, image_augmentations, image_data_augmentation, new_data_augmentation, pipeline, server, server_utils, video_server

def __getattr__(name: str) -> Any: ...