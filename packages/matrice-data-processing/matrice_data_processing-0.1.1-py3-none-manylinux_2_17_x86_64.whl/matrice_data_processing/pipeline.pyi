"""Auto-generated stub for module: pipeline."""
from typing import Any, Dict, List, Optional

from queue import Queue, Empty
import logging
import threading
import time

# Classes
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

