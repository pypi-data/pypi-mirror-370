import threading
import time
import logging
import uuid
from datetime import datetime
from typing import Dict
from ..services.WorkerSourcePipelineClient import WorkerSourcePipelineClient
from ..services.GrpcClientManager import GrpcClientManager
from ..repositories.DatasetSourceRepository import DatasetSourceRepository

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class DatasetSourceThread:
    """Individual thread for handling a single dataset source."""
    
    def __init__(self, dataset_source, pipeline_client, storage_path):
        self.dataset_source = dataset_source
        self.pipeline_client = pipeline_client
        self.storage_path = storage_path
        self.thread = None
        self.stop_event = threading.Event()
        self.last_frame_time = 0
        self.lock = threading.Lock()
        
        # Create storage directory for this dataset source
        self.dataset_storage_path = storage_path / "dataset_frames" / dataset_source.id
        self.dataset_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Track consecutive failures
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        
    def start(self):
        """Start the dataset source thread."""
        if self.thread and self.thread.is_alive():
            logger.warning(f"⚠️ [APP] Thread for dataset source {self.dataset_source.id} is already running.")
            return
            
        self.stop_event.clear()
        self.consecutive_failures = 0  # Reset failure counter
        self.thread = threading.Thread(
            target=self._run, 
            daemon=True,
            name=f"DatasetSource-{self.dataset_source.id}"
        )
        self.thread.start()
        logger.info(f"🚀 [APP] Started thread for dataset source {self.dataset_source.id} ({self.dataset_source.dataset_name})")
        
    def stop(self):
        """Stop the dataset source thread."""
        if not self.thread or not self.thread.is_alive():
            return
            
        self.stop_event.set()
        safe_join_thread(self.thread)
        logger.info(f"🛑 [APP] Stopped thread for dataset source {self.dataset_source.id}")
        
    def _run(self):
        """Main loop for this dataset source."""
        try:
            while not self.stop_event.is_set():
                current_time = time.time()
                
                # Check if it's time to capture a frame
                if (current_time - self.last_frame_time) >= self.dataset_source.sampling_interval:
                    success = self._capture_frame()
                    
                    with self.lock:
                        self.last_frame_time = current_time
                        if success:
                            self.consecutive_failures = 0  # Reset on success
                        else:
                            self.consecutive_failures += 1
                            
                    # If too many consecutive failures, log warning and pause
                    if self.consecutive_failures >= self.max_consecutive_failures:
                        logger.warning(f"⚠️ [APP] Dataset source {self.dataset_source.id} has {self.consecutive_failures} consecutive failures. Pausing for 30 seconds.")
                        time.sleep(30)  # Pause for 30 seconds
                        self.consecutive_failures = 0  # Reset after pause
                
                # Sleep for a shorter interval to be more responsive
                time.sleep(min(1, self.dataset_source.sampling_interval / 10))
                
        except Exception as e:
            logger.error(f"🚨 [APP] Error in dataset source thread {self.dataset_source.id}: {e}", exc_info=True)
            
    def _capture_frame(self):
        """Capture and save a frame for this dataset source. Returns True if successful."""
        try:
            # Get frame from source
            frame_bytes = self._get_frame_from_source(self.dataset_source.worker_source_url)
            
            if frame_bytes:
                # Generate unique filename
                timestamp = int(time.time() * 1000)
                frame_uuid = str(uuid.uuid4())
                filename = f"{frame_uuid}_{timestamp}.jpg"
                file_path = self.dataset_storage_path / filename
                
                # Save frame to local storage
                with open(file_path, 'wb') as f:
                    f.write(frame_bytes)
                
                # Create metadata file
                metadata = {
                    "dataset_source_id": self.dataset_source.id,
                    "dataset_id": self.dataset_source.dataset_id,
                    "worker_source_id": self.dataset_source.worker_source_id,
                    "dataset_name": self.dataset_source.dataset_name,
                    "worker_source_name": self.dataset_source.worker_source_name,
                    "worker_source_url": self.dataset_source.worker_source_url,
                    "frame_uuid": frame_uuid,
                    "timestamp": timestamp,
                    "captured_at": datetime.utcnow().isoformat()
                }
                
                metadata_path = file_path.with_suffix('.json')
                import json
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"📸 [APP] Captured frame for {self.dataset_source.dataset_name} (ID: {self.dataset_source.id})")
                return True
            else:
                logger.warning(f"⚠️ [APP] Could not get frame from source {self.dataset_source.worker_source_url}")
                return False
                
        except Exception as e:
            logger.error(f"🚨 [APP] Error capturing frame for {self.dataset_source.dataset_name}: {e}", exc_info=True)
            return False
            
    def _get_frame_from_source(self, source_url):
        """Get a frame from the given source URL."""
        try:
            stream_type = self.pipeline_client._detect_stream_type(source_url)
            if stream_type == "video_file":
                logger.info(f"🎬 [APP] Capturing video frame from {source_url}")
            elif stream_type == "image_file":
                logger.info(f"🖼️ [APP] Capturing image frame from {source_url}")
            elif stream_type in ["rtsp", "hls"]:
                logger.info(f"📡 [APP] Capturing live stream frame from {source_url}")
            
            frame_bytes = self.pipeline_client._get_single_frame_bytes(source_url)
            
            if frame_bytes and stream_type == "video_file":
                status = self.pipeline_client.get_video_positions_status()
                for video_path, info in status.items():
                    if info["duration"]:
                        logger.info(f"📊 [APP] Video progress: {info['progress_percent']:.1f}% ({info['current_position']:.2f}s / {info['duration']:.2f}s)")
            
            return frame_bytes
        except Exception as e:
            logger.error(f"🚨 [APP] Error getting frame from source {source_url}: {e}", exc_info=True)
            return None

class DatasetFrameWorker:
    def __init__(self, config: dict):
        """
        Initialize Dataset Frame Worker.

        Args:
            config (dict): Configuration object containing settings.
        """
        if not isinstance(config, dict):
            raise ValueError("⚠️ [APP] config must be a dictionary.")

        self.config = config
        self.worker_id = self.config.get("worker_id")
        self.server_host = self.config.get("server_host")
        self.token = self.config.get("token")

        if not self.worker_id:
            raise ValueError("⚠️ [APP] Configuration is missing 'worker_id'.")
        if not self.token:
            raise ValueError("⚠️ [APP] Configuration is missing 'token'.")

        self.dataset_source_repo = DatasetSourceRepository()
        
        # Get shared client instance from the centralized manager
        self.client_manager = GrpcClientManager.get_instance()
        self.worker_source_pipeline_client = self.client_manager.get_client(WorkerSourcePipelineClient)

        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Cache for dataset source threads
        self.dataset_source_threads: Dict[str, DatasetSourceThread] = {}
        self.last_sync_time = 0
        self.sync_interval = 30  # Sync dataset sources every 30 seconds
        
        # Thread for syncing dataset sources
        self.sync_thread = None
        
        # Sync lock to prevent multiple simultaneous sync operations
        self.sync_lock = threading.Lock()
        
        # Storage path for dataset frames
        from ..database.DatabaseManager import get_storage_path
        self.storage_path = get_storage_path("files")

    def start(self):
        """Start the Dataset Frame Worker."""
        with self.lock:
            if self.thread and self.thread.is_alive():
                logger.warning("⚠️ [APP] Dataset Frame Worker is already running.")
                return

            self.stop_event.clear()
            
            # Start sync thread
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()
            
            # Start main worker thread
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"🚀 [APP] Dataset Frame Worker started (Device: {self.worker_id}).")

    def stop(self):
        """Stop the Dataset Frame Worker."""
        with self.lock:
            if not self.thread or not self.thread.is_alive():
                logger.warning("⚠️ [APP] Dataset Frame Worker is not running.")
                return

            self.stop_event.set()
            
            # Stop all dataset source threads
            for thread in self.dataset_source_threads.values():
                thread.stop()
            
            # Wait for threads to stop
            if self.thread:
                safe_join_thread(self.thread)
            if self.sync_thread:
                safe_join_thread(self.sync_thread)
                
            self.thread = None
            self.sync_thread = None
            logger.info(f"🛑 [APP] Dataset Frame Worker stopped (Device: {self.worker_id}).")

    def _run(self):
        """Main loop for managing dataset source threads."""
        try:
            while not self.stop_event.is_set():
                self._manage_dataset_source_threads()
                time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            logger.error("🚨 [APP] Unexpected error in Dataset Frame Worker main loop.", exc_info=True)

    def _sync_loop(self):
        """Background thread for syncing dataset sources."""
        try:
            while not self.stop_event.is_set():
                self._sync_dataset_sources()
                time.sleep(self.sync_interval)
        except Exception as e:
            logger.error("🚨 [APP] Error in dataset source sync loop.", exc_info=True)

    def _sync_dataset_sources(self):
        """Sync dataset sources from server."""
        # Prevent multiple simultaneous sync operations
        if not self.sync_lock.acquire(blocking=False):
            logger.debug("🔄 [APP] Sync operation already in progress, skipping...")
            return
            
        try:
            from ..services.DatasetSourceClient import DatasetSourceClient
            # Use shared client instead of creating new instance
            client = self.client_manager.get_client(DatasetSourceClient, "DatasetSourceClient")
            response = client.get_dataset_source_list(self.token)
            
            if response and response.get("success"):
                dataset_sources_data = response.get("data", [])
                self.dataset_source_repo.sync_dataset_sources(dataset_sources_data)
                self.last_sync_time = time.time()
            else:
                error_message = response.get("message", "Unknown error") if response else "Unknown error"
                logger.error(f"❌ [APP] Failed to sync dataset sources: {error_message}")

        except Exception as e:
            logger.error("🚨 [APP] Error syncing dataset sources.", exc_info=True)
        finally:
            self.sync_lock.release()

    def _cleanup_orphaned_frames(self, deleted_dataset_source_ids):
        """Clean up frames for deleted dataset sources."""
        try:
            for dataset_source_id in deleted_dataset_source_ids:
                orphaned_frames_path = self.storage_path / "dataset_frames" / dataset_source_id
                if orphaned_frames_path.exists():
                    import shutil
                    shutil.rmtree(orphaned_frames_path)
                    logger.info(f"🗑️ [APP] Cleaned up orphaned frames for deleted dataset source {dataset_source_id}")
        except Exception as e:
            logger.error(f"🚨 [APP] Error cleaning up orphaned frames: {e}", exc_info=True)

    def _manage_dataset_source_threads(self):
        """Manage dataset source threads based on current dataset sources."""
        try:
            # Get current dataset sources from local database
            dataset_sources = self.dataset_source_repo.get_all_dataset_sources()
            current_dataset_source_ids = {ds.id for ds in dataset_sources}
            
            # Stop threads for dataset sources that no longer exist
            threads_to_remove = []
            deleted_dataset_source_ids = []
            for dataset_source_id, thread in self.dataset_source_threads.items():
                if dataset_source_id not in current_dataset_source_ids:
                    logger.info(f"🛑 [APP] Stopping thread for deleted dataset source {dataset_source_id}")
                    thread.stop()
                    threads_to_remove.append(dataset_source_id)
                    deleted_dataset_source_ids.append(dataset_source_id)
                    
            for dataset_source_id in threads_to_remove:
                del self.dataset_source_threads[dataset_source_id]
            
            # Clean up orphaned frames for deleted dataset sources
            if deleted_dataset_source_ids:
                self._cleanup_orphaned_frames(deleted_dataset_source_ids)
            
            # Process current dataset sources
            for dataset_source in dataset_sources:
                if dataset_source.id not in self.dataset_source_threads:
                    # Create new thread for new dataset source
                    logger.info(f"🆕 [APP] Creating new thread for dataset source {dataset_source.id} ({dataset_source.dataset_name})")
                    thread = DatasetSourceThread(
                        dataset_source=dataset_source,
                        pipeline_client=self.worker_source_pipeline_client,
                        storage_path=self.storage_path
                    )
                    self.dataset_source_threads[dataset_source.id] = thread
                    thread.start()
                else:
                    # Update existing thread with new dataset source data
                    existing_thread = self.dataset_source_threads[dataset_source.id]
                    if self._dataset_source_changed(existing_thread.dataset_source, dataset_source):
                        logger.info(f"🔄 [APP] Updating thread for dataset source {dataset_source.id} ({dataset_source.dataset_name})")
                        # Stop the old thread
                        existing_thread.stop()
                        # Create new thread with updated data
                        new_thread = DatasetSourceThread(
                            dataset_source=dataset_source,
                            pipeline_client=self.worker_source_pipeline_client,
                            storage_path=self.storage_path
                        )
                        self.dataset_source_threads[dataset_source.id] = new_thread
                        new_thread.start()
            
            # Log current status
            active_threads = len([t for t in self.dataset_source_threads.values() if t.thread and t.thread.is_alive()])
            logger.debug(f"📊 [APP] Dataset Frame Worker status: {active_threads} active threads, {len(dataset_sources)} total dataset sources")
                    
        except Exception as e:
            logger.error("🚨 [APP] Error managing dataset source threads.", exc_info=True)

    def _dataset_source_changed(self, old_dataset_source, new_dataset_source):
        """Check if dataset source data has changed significantly."""
        try:
            # Compare relevant fields that would affect thread behavior
            fields_to_compare = [
                'worker_source_url',
                'sampling_interval',
                'dataset_name',
                'worker_source_name',
                'dataset_id',
                'worker_source_id'
            ]
            
            for field in fields_to_compare:
                old_value = getattr(old_dataset_source, field, None)
                new_value = getattr(new_dataset_source, field, None)
                if old_value != new_value:
                    logger.debug(f"🔄 [APP] Dataset source {new_dataset_source.id} field '{field}' changed: {old_value} -> {new_value}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"🚨 [APP] Error comparing dataset sources: {e}", exc_info=True)
            return True  # Assume changed if comparison fails

    def get_status(self):
        """Get current status of dataset frame worker."""
        try:
            dataset_sources = self.dataset_source_repo.get_all_dataset_sources()
            active_threads = [t for t in self.dataset_source_threads.values() if t.thread and t.thread.is_alive()]
            
            return {
                "total_dataset_sources": len(dataset_sources),
                "active_threads": len(active_threads),
                "thread_details": [
                    {
                        "dataset_source_id": t.dataset_source.id,
                        "dataset_name": t.dataset_source.dataset_name,
                        "is_alive": t.thread.is_alive() if t.thread else False,
                        "consecutive_failures": t.consecutive_failures
                    }
                    for t in self.dataset_source_threads.values()
                ]
            }
        except Exception as e:
            logger.error(f"🚨 [APP] Error getting dataset frame worker status: {e}", exc_info=True)
            return {"error": str(e)} 