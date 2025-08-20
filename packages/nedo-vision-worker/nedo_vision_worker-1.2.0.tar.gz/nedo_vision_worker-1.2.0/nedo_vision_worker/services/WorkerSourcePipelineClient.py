import logging
import os
import time
import ffmpeg
from urllib.parse import urlparse
from pathlib import Path

from ..database.DatabaseManager import _get_storage_paths
from ..repositories.WorkerSourcePipelineDebugRepository import WorkerSourcePipelineDebugRepository
from ..repositories.WorkerSourcePipelineDetectionRepository import WorkerSourcePipelineDetectionRepository
from .GrpcClientBase import GrpcClientBase
from .SharedDirectDeviceClient import SharedDirectDeviceClient
from ..protos.WorkerSourcePipelineService_pb2_grpc import WorkerSourcePipelineServiceStub
from ..protos.WorkerSourcePipelineService_pb2 import GetListByWorkerIdRequest, SendPipelineImageRequest, UpdatePipelineStatusRequest, SendPipelineDebugRequest, SendPipelineDetectionDataRequest
from ..repositories.WorkerSourcePipelineRepository import WorkerSourcePipelineRepository


class WorkerSourcePipelineClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        super().__init__(server_host, server_port)
        self.repo = WorkerSourcePipelineRepository()
        self.debug_repo = WorkerSourcePipelineDebugRepository()
        self.detection_repo = WorkerSourcePipelineDetectionRepository()
        storage_paths = _get_storage_paths()
        self.source_file_path = storage_paths["files"] / "source_files"
        self.shared_device_client = SharedDirectDeviceClient()
        
        # Track video playback positions and last fetch times
        self.video_positions = {}  # {video_path: current_position_in_seconds}
        self.last_fetch_times = {}  # {video_path: last_fetch_timestamp}

        try:
            self.connect(WorkerSourcePipelineServiceStub)
        except Exception as e:
            logging.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None

    def _detect_stream_type(self, url):
        if isinstance(url, str) and url.isdigit():
            return "direct"
        
        parsed_url = urlparse(url)
        if parsed_url.scheme == "rtsp":
            return "rtsp"
        elif parsed_url.scheme in ["http", "https"] and url.endswith(".m3u8"):
            return "hls"
        elif url.startswith("worker-source/"):
            file_path = self.source_file_path / os.path.basename(url)
            if file_path.exists():
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
                if file_path.suffix.lower() in video_extensions:
                    return "video_file"
            return "image_file"
        else:
            return "unknown"
    
    def _get_video_duration(self, file_path):
        """Get the duration of a video file in seconds."""
        try:
            file_path_str = str(file_path)
            if not os.path.exists(file_path_str):
                logging.error(f"Video file does not exist: {file_path_str}")
                return None
            import subprocess
            import json
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                file_path_str
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logging.error(f"FFprobe failed for {file_path_str}: {result.stderr}")
                return None
            try:
                probe_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse ffprobe output for {file_path_str}: {e}")
                return None
            if 'format' not in probe_data or 'duration' not in probe_data['format']:
                logging.error(f"No duration found in probe result for {file_path_str}")
                return None
            duration = probe_data['format']['duration']
            # Defensive: ensure duration is a float or convertible to float
            try:
                duration_val = float(duration)
            except Exception as e:
                logging.error(f"Duration value not convertible to float: {duration} ({type(duration)}) - {e}", exc_info=True)
                return None
            if isinstance(duration_val, bool):
                logging.error(f"Duration value is boolean, which is invalid: {duration_val}")
                return None
            return duration_val
        except Exception as e:
            logging.error(f"Error getting video duration for {file_path}: {e}", exc_info=True)
            return None
    
    def _get_current_video_position(self, video_path):
        """Get or advance the current playback position for a video file based on real time elapsed."""
        current_time = time.time()
        
        if video_path not in self.video_positions:
            self.video_positions[video_path] = 0.0
            self.last_fetch_times[video_path] = current_time
            return 0.0
        
        current_pos = self.video_positions[video_path]
        last_fetch_time = self.last_fetch_times[video_path]
        
        # Calculate time elapsed since last fetch
        time_elapsed = current_time - last_fetch_time
        
        # Advance position by the actual time elapsed
        current_pos += time_elapsed
        
        # Get video duration to handle looping
        duration = self._get_video_duration(video_path)
        if duration is not None and isinstance(duration, (int, float)):
            # Loop back to beginning if we've reached the end
            if current_pos >= duration:
                current_pos = 0.0
        else:
            # Default to 120 seconds if we can't get duration
            if current_pos >= 120.0:
                current_pos = 0.0
        
        # Update the stored position and fetch time
        self.video_positions[video_path] = current_pos
        self.last_fetch_times[video_path] = current_time
        
        return current_pos
    
    def reset_video_position(self, video_path):
        """Reset the playback position for a specific video file."""
        if video_path in self.video_positions:
            self.video_positions[video_path] = 0.0
            self.last_fetch_times[video_path] = time.time()
            logging.info(f"Reset video position for {video_path}")
    
    def reset_all_video_positions(self):
        """Reset all video playback positions."""
        self.video_positions.clear()
        self.last_fetch_times.clear()
        logging.info("Reset all video positions")
    
    def get_video_positions_status(self):
        """Get the current status of all video positions for debugging."""
        status = {}
        for video_path, position in self.video_positions.items():
            duration = self._get_video_duration(video_path)
            last_fetch_time = self.last_fetch_times.get(video_path, None)
            time_since_last_fetch = time.time() - last_fetch_time if last_fetch_time else None
            
            if duration:
                progress = (position / duration) * 100
                status[video_path] = {
                    "current_position": position,
                    "duration": duration,
                    "progress_percent": progress,
                    "last_fetch_time": last_fetch_time,
                    "time_since_last_fetch": time_since_last_fetch
                }
            else:
                status[video_path] = {
                    "current_position": position,
                    "duration": None,
                    "progress_percent": None,
                    "last_fetch_time": last_fetch_time,
                    "time_since_last_fetch": time_since_last_fetch
                }
        return status
    
    def _get_single_frame_bytes(self, url):
        stream_type = self._detect_stream_type(url)
        
        if stream_type == "direct":
            device_index = int(url)
            logging.info(f"📹 [APP] Capturing frame from direct video device: {device_index}")
            
            # Use the shared device client for direct devices
            try:
                # Get device properties first
                width, height, fps, pixel_format = self.shared_device_client.get_video_properties(url)
                if not width or not height:
                    logging.error(f"Failed to get properties for device {device_index}")
                    return None
                
                # Create ffmpeg input using shared device client
                ffmpeg_input = self.shared_device_client.create_ffmpeg_input(url, width, height, fps)
                
            except Exception as e:
                logging.error(f"Error setting up direct device {device_index}: {e}")
                return None
        elif stream_type == "rtsp":
            ffmpeg_input = (
                ffmpeg
                .input(url, rtsp_transport="tcp", fflags="nobuffer", timeout="5000000")
            )
        elif stream_type == "hls":
            ffmpeg_input = (
                ffmpeg
                .input(url, format="hls", analyzeduration="10000000", probesize="10000000")
            )
        elif stream_type == "video_file":
            file_path = self.source_file_path / os.path.basename(url)
            file_path_str = str(file_path)
            
            if not os.path.exists(file_path_str):
                logging.error(f"Video file does not exist: {file_path_str}")
                return None
            
            current_position = self._get_current_video_position(file_path_str)
            logging.info(f"🎬 [APP] Capturing video frame at position {current_position:.2f}s from {file_path_str}")
            
            ffmpeg_input = (
                ffmpeg
                .input(file_path_str, ss=current_position)
            )
        elif stream_type == "image_file":
            file_path = self.source_file_path / os.path.basename(url)
            logging.info(f"🖼️ [APP] Capturing image frame from {file_path}")
            
            ffmpeg_input = (
                ffmpeg
                .input(str(file_path))
            )   
        else:
            logging.error(f"Unsupported stream type: {url}")
            return None

        if stream_type == "video_file":
            process = (
                ffmpeg_input
                .output('pipe:', format='mjpeg', vframes=1, q=2)
                .overwrite_output()
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )
        else:
            process = (
                ffmpeg_input
                .output('pipe:', format='mjpeg', vframes=1, q=2)
                .overwrite_output()
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )
            
        try:    
            stdout, stderr = process.communicate(timeout=15)
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logging.error(f"FFmpeg error: {error_msg}")
                return None
            
            if not stdout:
                logging.error("No data received from FFmpeg")
                return None
        
            return stdout
        
        except Exception as e:
            logging.error(f"Error capturing frame: {e}", exc_info=True)
            return None
        
        finally:
            # Release device access for direct devices
            if stream_type == "direct":
                self.shared_device_client.release_device_access(url)
            
            process.terminate()
            process.wait()

    def update_pipeline_status(self, pipeline_id: str, status_code: str, token: str):
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            timestamp = int(time.time() * 1000)

            request = UpdatePipelineStatusRequest(
                pipeline_id=pipeline_id,
                status_code=status_code,
                timestamp=timestamp,
                token=token
            )
            response = self.handle_rpc(self.stub.UpdateStatus, request)

            if response and response.success:
                return {"success": True, "message": response.message}
            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error updating pipeline status: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}

    def get_worker_source_pipeline_list(self, worker_id: str, token: str) -> dict:
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            request = GetListByWorkerIdRequest(worker_id=worker_id, token=token)
            response = self.handle_rpc(self.stub.GetListByWorkerId, request)

            if response and response.success:
                # Create a wrapper function that captures the token
                def update_status_callback(pipeline_id: str, status_code: str):
                    return self.update_pipeline_status(pipeline_id, status_code, token)
                
                self.repo.sync_worker_source_pipelines(response, update_status_callback)  # Sync includes delete, update, insert
                return {"success": True, "message": response.message, "data": response.data}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error fetching worker source pipeline list: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}
        
    def send_pipeline_image(self, worker_source_pipeline_id: str, uuid: str, url: str, token: str):
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            frame_bytes = self._get_single_frame_bytes(url)
            
            if not frame_bytes:
                return {"success": False, "message": "Failed to retrieve frame from source"}
            
            request = SendPipelineImageRequest(
                worker_source_pipeline_id=worker_source_pipeline_id,
                uuid=uuid,
                image=frame_bytes,
                token=token
            )
            response = self.handle_rpc(self.stub.SendPipelineImage, request)

            if response and response.success:
                return {"success": True, "message": response.message}
            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error sending pipeline image: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}
        
    @staticmethod
    def read_image_as_binary(image_path: str) -> bytes:
        """
        Reads an image file and returns its binary content.

        Args:
            image_path (str): Path to the image file.

        Returns:
            bytes: Binary content of the image.
        """
        with open(image_path, 'rb') as image_file:
            return image_file.read()
        
    def sync_pipeline_debug(self, token: str):
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            debug_entries = self.debug_repo.get_debug_entries_with_data()
            
            for debug_entry in debug_entries:
                image_binary = self.read_image_as_binary(debug_entry.image_path)

                request = SendPipelineDebugRequest(
                    worker_source_pipeline_id=debug_entry.worker_source_pipeline_id,
                    uuid=debug_entry.uuid,
                    data=debug_entry.data,
                    image=image_binary,
                    token=token
                )
                response = self.handle_rpc(self.stub.SendPipelineDebug, request)

                if response and response.success:
                    self.debug_repo.delete_entry_by_id(debug_entry.id)
                else:
                    return {"success": False, "message": response.message if response else "Unknown error"}

            return {"success": True, "message": "Successfully synced debug entries"}

        except Exception as e:
            logging.error(f"Error syncing pipeline debug: {e}")

    def sync_pipeline_detection(self, token: str):
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            entries = self.detection_repo.get_entries()
            
            for entry in entries:
                image_binary = self.read_image_as_binary(entry.image_path)

                request = SendPipelineDetectionDataRequest(
                    worker_source_pipeline_id=entry.worker_source_pipeline_id,
                    data=entry.data,
                    image=image_binary,
                    timestamp=int(entry.created_at.timestamp() * 1000),
                    token=token
                )
                response = self.handle_rpc(self.stub.SendPipelineDetectionData, request)

                if response and response.success:
                    self.detection_repo.delete_entry_by_id(entry.id)
                else:
                    return {"success": False, "message": response.message if response else "Unknown error"}

            return {"success": True, "message": "Successfully synced debug entries"}

        except Exception as e:
            logging.error(f"Error syncing pipeline debug: {e}")