"""Auto-generated stub for module: image_data_augmentation."""
from typing import Any, Dict, List, Optional, Set, Tuple

from abc import ABC, abstractmethod
from augmentation_utils.strategies import *
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from kafka import KafkaProducer, KafkaConsumer
from math import comb
from pipeline import Pipeline
from queue import Queue, Empty
from scipy.special import softmax
from urllib.parse import urlparse
import albumentations as A
import cv2
import json
import logging
import math
import numpy as np
import random
import requests
import threading
import time
import traceback

# Constants
MIN_DIM: float

# Functions
def apply_augmentations_stage(dataset_item: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...
def completion_monitor_stage(dataset_item: Any, probability_manager: Any, pipeline_config: Any, **kwargs: Any) -> Any: ...
def create_probability_based_augmentation_pipeline(pipeline_config: Any, kafka_config: Dict[str, Any]) -> Optional[Pipeline]: ...
def download_images_stage(dataset_item: Any, upload_url_manager: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...
def fetch_dataset_items_stage(dataset_item: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...
def fetch_upload_urls_stage(dataset_item: Any, pipeline_config: Any, upload_url_manager: Any, probability_manager: Any, **kwargs: Any) -> Any: ...
def get_kafka_brokers() -> Any: ...
def get_object_key_from_url(source_url: str) -> str: ...
def parse_dynamic_pipeline_config(config_data: Dict, source_dataset_version: str = 'v1.0', target_dataset_version: str = 'v1.1') -> Any: ...
    """
    Parse dynamic pipeline configuration from input data
    """
def upload_and_publish_stage(dataset_item: Any, new_items_producer: Any, new_items_topic: Any, pipeline_config: Any, probability_manager: Any, **kwargs: Any) -> Any: ...

# Classes
class AugmentationStep:
    """
    Represents a single augmentation step
    """

    pass
class AugmentationStrategyFactory:
    """
    Factory class to create augmentation strategy instances
    """

    STRATEGIES: Dict[Any, Any]

    def create_strategy(cls: Any, aug_step: Any) -> Any: ...

class DynamicPipelineConfig:
    """
    Configuration for dynamic augmentation pipeline
    """

    pass
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

class ImageAugmentationStrategy(ABC):
    """
    Base class for image augmentation strategies
    """

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

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

class PaginatedDataManager:
    """
    Manages paginated data requests and responses
    """

    def __init__(self: Any, request_topic: str, response_topic: str, bootstrap_servers: str, consumer_group: str = 'augmentation_pipeline_consumer', page_size: int = 100, max_retries: int = 3, retry_delay: int = 5) -> None: ...

    def check_for_responses(self: Any, expected_augmentation_id: str = None) -> List[ImageDataItem]: ...

    def is_pagination_complete(self: Any) -> bool: ...

    def request_page(self: Any, page_number: int, dataset_id: str = None, augmentation_id: str = None, source_version: str = 'v1.0', **kwargs: Any) -> bool: ...

class UploadURLManager:
    """
    Manages upload URL requests and responses
    """

    def __init__(self: Any, request_topic: str, response_topic: str, bootstrap_servers: str, consumer_group: str = 'upload_url_consumer') -> None: ...

    def close(self: Any) -> Any: ...

    def get_upload_url(self: Any, timeout_seconds: int = 60, expected_augmentation_id: str = None) -> Optional[str]: ...

    def has_pending_requests(self: Any) -> bool: ...

    def request_upload_url(self: Any, dataset_id: str, augmentation_id: str = None) -> bool: ...

