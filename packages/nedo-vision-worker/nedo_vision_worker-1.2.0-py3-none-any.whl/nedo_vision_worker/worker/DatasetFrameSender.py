import os
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional
from ..services.DatasetSourceClient import DatasetSourceClient
from ..database.DatabaseManager import _get_storage_paths

logger = logging.getLogger(__name__)

class DatasetFrameSender:
    """Handles batched sending of saved dataset frames to the backend."""
    
    def __init__(self, server_host: str, token: str):
        """
        Initialize the Dataset Frame Sender.
        
        Args:
            server_host (str): Server host for sending frames
            token (str): Authentication token
        """
        self.server_host = server_host
        self.token = token
        self.client = DatasetSourceClient(server_host)
        
        # Get storage paths
        storage_paths = _get_storage_paths()
        self.dataset_frames_path = storage_paths["files"] / "dataset_frames"
        
        # Track sent frames to avoid duplicates
        self.sent_frames = set()
        
    def send_pending_frames(self, max_batch_size: int = 10) -> Dict[str, int]:
        """
        Send pending dataset frames in batches.
        
        Args:
            max_batch_size (int): Maximum number of frames to send in one batch
            
        Returns:
            Dict[str, int]: Statistics of sent frames per dataset source
        """
        stats = {}
        
        try:
            if not self.dataset_frames_path.exists():
                return stats
                
            # Find all dataset source directories
            for dataset_source_dir in self.dataset_frames_path.iterdir():
                if not dataset_source_dir.is_dir():
                    continue
                    
                dataset_source_id = dataset_source_dir.name
                sent_count = self._send_frames_for_dataset_source(
                    dataset_source_dir, 
                    dataset_source_id, 
                    max_batch_size
                )
                
                if sent_count > 0:
                    stats[dataset_source_id] = sent_count
                    
        except Exception as e:
            logger.error(f"🚨 [APP] Error sending pending frames: {e}")
            
        return stats
        
    def _send_frames_for_dataset_source(self, dataset_source_dir: Path, dataset_source_id: str, max_batch_size: int) -> int:
        """
        Send frames for a specific dataset source.
        
        Args:
            dataset_source_dir (Path): Directory containing frames for this dataset source
            dataset_source_id (str): ID of the dataset source
            max_batch_size (int): Maximum frames to send in one batch
            
        Returns:
            int: Number of frames sent
        """
        sent_count = 0
        
        try:
            # Find all frame files (jpg) that haven't been sent yet
            frame_files = []
            for file_path in dataset_source_dir.glob("*.jpg"):
                frame_uuid = file_path.stem.split('_')[0]  # Extract UUID from filename
                
                if frame_uuid not in self.sent_frames:
                    metadata_path = file_path.with_suffix('.json')
                    if metadata_path.exists():
                        frame_files.append((file_path, metadata_path, frame_uuid))
                        
            # Sort by timestamp (filename contains timestamp)
            frame_files.sort(key=lambda x: x[0].name)
            
            # Send frames in batches
            for i in range(0, len(frame_files), max_batch_size):
                batch = frame_files[i:i + max_batch_size]
                if self._send_frame_batch(batch, dataset_source_id):
                    sent_count += len(batch)
                    
        except Exception as e:
            logger.error(f"🚨 [APP] Error sending frames for dataset source {dataset_source_id}: {e}")
            
        return sent_count
        
    def _send_frame_batch(self, frame_batch: List[tuple], dataset_source_id: str) -> bool:
        """
        Send a batch of frames to the backend.
        
        Args:
            frame_batch (List[tuple]): List of (file_path, metadata_path, frame_uuid) tuples
            dataset_source_id (str): ID of the dataset source
            
        Returns:
            bool: True if batch was sent successfully
        """
        try:
            for file_path, metadata_path, frame_uuid in frame_batch:
                # Read frame data
                with open(file_path, 'rb') as f:
                    frame_bytes = f.read()
                    
                # Read metadata
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    
                # Send frame to backend
                response = self.client.send_dataset_frame(
                    dataset_source_id=metadata["dataset_source_id"],
                    uuid=metadata["frame_uuid"],
                    image=frame_bytes,
                    timestamp=metadata["timestamp"],
                    token=self.token
                )
                
                if response and response.get("success"):
                    # Mark as sent and clean up local files
                    self.sent_frames.add(frame_uuid)
                    self._cleanup_sent_frame(file_path, metadata_path)
                    logger.debug(f"✅ [APP] Sent frame {frame_uuid} for dataset source {dataset_source_id}")
                else:
                    error_message = response.get("message", "Unknown error") if response else "Unknown error"
                    
                    # Handle specific error cases
                    if "DatasetSource not found" in error_message:
                        logger.warning(f"🗑️ [APP] Dataset source {dataset_source_id} not found, cleaning up orphaned frame {frame_uuid}")
                        # Mark as sent to avoid retry loops and clean up
                        self.sent_frames.add(frame_uuid)
                        self._cleanup_sent_frame(file_path, metadata_path)
                    else:
                        logger.error(f"❌ [APP] Failed to send frame {frame_uuid}: {error_message}")
                        return False
                    
            return True
            
        except Exception as e:
            logger.error(f"🚨 [APP] Error sending frame batch: {e}")
            return False
            
    def _cleanup_sent_frame(self, file_path: Path, metadata_path: Path):
        """
        Clean up local files after successful send.
        
        Args:
            file_path (Path): Path to the frame file
            metadata_path (Path): Path to the metadata file
        """
        try:
            # Remove frame file
            if file_path.exists():
                file_path.unlink()
                
            # Remove metadata file
            if metadata_path.exists():
                metadata_path.unlink()
                
        except Exception as e:
            logger.error(f"🚨 [APP] Error cleaning up sent frame: {e}")
            
    def get_pending_frame_count(self) -> int:
        """
        Get the total number of pending frames to be sent.
        
        Returns:
            int: Number of pending frames
        """
        pending_count = 0
        
        try:
            if not self.dataset_frames_path.exists():
                return 0
                
            for dataset_source_dir in self.dataset_frames_path.iterdir():
                if not dataset_source_dir.is_dir():
                    continue
                    
                for file_path in dataset_source_dir.glob("*.jpg"):
                    frame_uuid = file_path.stem.split('_')[0]
                    if frame_uuid not in self.sent_frames:
                        pending_count += 1
                        
        except Exception as e:
            logger.error(f"🚨 [APP] Error counting pending frames: {e}")
            
        return pending_count 