import logging
import threading
from datetime import datetime, timezone
import os
from ..database.DatabaseManager import _get_storage_paths
from ..repositories.WorkerSourceRepository import WorkerSourceRepository
from .WorkerSourceClient import WorkerSourceClient
from .GrpcClientManager import GrpcClientManager
from ..util.VideoProbeUtil import VideoProbeUtil  # Helper to extract video metadata

logger = logging.getLogger(__name__)

class WorkerSourceUpdater:
    """Handles synchronization and updates of worker sources via gRPC and local database.
    
    This class is thread-safe and can be used concurrently from multiple threads.
    """

    def __init__(self, server_host: str, token: str):
        storage_paths = _get_storage_paths()
        self.source_file_path = storage_paths["files"] / "source_files"
        # Use shared client instead of creating new instance
        self.client = GrpcClientManager.get_shared_client(WorkerSourceClient)
        self.repo = WorkerSourceRepository()
        self.token = token
        # Thread safety lock for critical operations
        self._lock = threading.RLock()

    def _get_source_metadata(self, source):
        if source.type_code == "live":
            url = source.url
        elif source.type_code == "direct":
            url = source.url
        else:
            url = source.file_path
            
        if not url:
            return None
        
        if source.type_code == "file":
            url = self.source_file_path / os.path.basename(url)
        
        return VideoProbeUtil.get_video_metadata(url)

    def update_worker_sources(self):
        """Fetch local worker sources, probe video URLs, and update if different from the local DB.
        
        This method is thread-safe and can be called concurrently from multiple threads.
        """
        with self._lock:
            try:
                worker_sources = self.repo.get_all_worker_sources()
                updated_records = []

                for source in worker_sources:
                    metadata = self._get_source_metadata(source)
                    if not metadata:
                        logger.warning(f"⚠️ [APP] Failed to probe video for Worker Source ID {source.id} (type: {source.type_code}, url: {source.url if hasattr(source, 'url') else 'N/A'})")
                        # Set disconnected status for failed probes
                        if source.status_code != "disconnected":
                            source.status_code = "disconnected"
                            source.resolution = None
                            source.frame_rate = None
                            updated_records.append(source)
                            
                            # Send gRPC update for disconnected status
                            worker_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                            response = self.client.update_worker_source(
                                worker_source_id=source.id,
                                resolution=None,
                                status_code="disconnected",
                                frame_rate=None,
                                worker_timestamp=worker_timestamp,
                                token=self.token,
                            )
                            
                            if response.get("success"):
                                logger.info(f"✅ [APP] Updated Worker Source ID {source.id} to disconnected")
                            else:
                                logger.error(f"🚨 [APP] Failed to update Worker Source ID {source.id} to disconnected: {response.get('message')}")
                        continue

                    # Extract details
                    resolution = metadata.get("resolution")
                    frame_rate = round(metadata.get("frame_rate"), 0) if metadata.get("frame_rate") else None
                    status_code = "connected" if resolution else "disconnected"
                    # .NET Compatible time
                    worker_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

                    # Compare with local database values
                    if (
                        source.resolution != resolution or
                        source.frame_rate != frame_rate or
                        source.status_code != status_code
                    ):
                        logger.info(f"🔄 [APP] Detected changes in Worker Source ID {source.id}, updating...")

                        # Update local database
                        source.resolution = resolution
                        source.frame_rate = frame_rate
                        source.status_code = status_code
                        updated_records.append(source)

                        # Send gRPC update request (client is thread-safe)
                        response = self.client.update_worker_source(
                            worker_source_id=source.id,
                            resolution=resolution,
                            status_code=status_code,
                            frame_rate=frame_rate,
                            worker_timestamp=worker_timestamp,
                            token=self.token,
                        )

                        if response.get("success"):
                            logger.info(f"✅ [APP] Updated Worker Source ID {source.id} - {response.get('message')}")
                        else:
                            logger.error(f"🚨 [APP] Failed to update Worker Source ID {source.id}: {response.get('message')}")

                # Batch update local database
                if updated_records:
                    self.repo.bulk_update_worker_sources(updated_records)

            except Exception as e:
                logger.error(f"🚨 [APP] Unexpected error while updating worker sources: {e}", exc_info=True)

    def stop_worker_sources(self):
        """Stop all worker sources.
        
        This method is thread-safe and can be called concurrently from multiple threads.
        """
        with self._lock:
            try:
                worker_sources = self.repo.get_all_worker_sources()
                updated_records = []

                for source in worker_sources:
                    source.status_code = "disconnected"
                    worker_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

                    updated_records.append(source)

                    # Send gRPC update request (client is thread-safe)
                    response = self.client.update_worker_source(
                        worker_source_id=source.id,
                        resolution=source.resolution,
                        status_code=source.status_code,
                        frame_rate=source.frame_rate,
                        worker_timestamp=worker_timestamp,
                        token=self.token,
                    )

                    if response.get("success"):
                        logger.info(f"✅ [APP] Updated Worker Source ID {source.id} - {response.get('message')}")
                    else:
                        logger.error(f"🚨 [APP] Failed to update Worker Source ID {source.id}: {response.get('message')}")

                # Batch update local database
                if updated_records:
                    self.repo.bulk_update_worker_sources(updated_records)
            except Exception as e:
                logger.error(f"🚨 [APP] Unexpected error while stopping worker sources: {e}", exc_info=True)