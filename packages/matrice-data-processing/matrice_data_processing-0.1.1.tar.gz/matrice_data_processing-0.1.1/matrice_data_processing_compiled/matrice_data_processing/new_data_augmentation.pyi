"""Auto-generated stub for module: new_data_augmentation."""
from typing import Any, Dict, List, Optional, Tuple

from abc import ABC, abstractmethod
from augmentation_utils.base import ImageAugmentationStrategy
from augmentation_utils.strategies import BlurAugmentation, BrightnessContrastAugmentation, HorizontalFlipAugmentation, RandomAffineAugmentation, ColorJitterAugmentation, HueSaturationValueAugmentation
from kafka import KafkaConsumer, KafkaProducer
from pipeline import Pipeline
from queue import Queue
import albumentations as A
import cv2
import json
import logging
import numpy as np
import requests
import time
import traceback

# Functions
def apply_augmentations_stage(augmentation_queue: Any, update_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 3: Apply augmentations to images
    """
def create_data_augmentation_pipeline(kafka_config: Dict[str, Any]) -> Optional[Pipeline]: ...
    """
    Create and configure the data augmentation pipeline
    
    Args:
        kafka_config: Configuration for Kafka consumer/producer
    
    Returns:
        Configured Pipeline instance
    """
def download_images_stage(download_queue: Any, augmentation_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 2: Download images from S3 URLs
    """
def fetch_dataset_items_stage(dataset_items_queue: Any, download_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 1: Fetch dataset items from input queue
    This is essentially a pass-through stage that can add any preprocessing if needed
    """
def kafka_consumer_producer(consumer_topic: str, producer_topic: str, bootstrap_servers: List[str], dataset_items_queue: Any, output_queue: Any, consumer_group: str = 'augmentation_pipeline') -> Any: ...
    """
    Kafka consumer to populate input queue and producer to publish output
    """
def update_and_upload_stage(update_queue: Any, output_queue: Any, **kwargs: Any) -> Any: ...
    """
    Stage 4: Update dataset item metadata and upload augmented image to S3
    """

# Classes
class AugmentationStrategyFactory:
    """
    Factory class to create augmentation strategy instances
    """

    STRATEGIES: Dict[Any, Any]

    def create_strategy(cls: Any, aug_config: Dict) -> Any: ...
        """
        Create augmentation strategy from configuration
        """

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

