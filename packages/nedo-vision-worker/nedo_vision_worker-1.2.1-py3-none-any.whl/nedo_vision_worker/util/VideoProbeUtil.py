import cv2
import subprocess
import logging
import json
import fractions
import shutil
import sys
import platform
from pathlib import Path
from urllib.parse import urlparse
from .FFmpegUtil import get_rtsp_probe_options


try:
    from nedo_vision_worker.services.VideoSharingDaemon import VideoSharingClient
except ImportError:
    logging.warning("VideoSharingDaemon not available")
    VideoSharingClient = None

# Import DatabaseManager for storage path
try:
    from nedo_vision_worker.database.DatabaseManager import get_storage_path
except ImportError:
    get_storage_path = None

class VideoProbeUtil:
    """Utility to extract metadata from video URLs using OpenCV and ffmpeg."""
    
    @staticmethod
    def get_video_metadata(video_url: str) -> dict:
        try:
            if isinstance(video_url, str) and video_url.isdigit():
                metadata = VideoProbeUtil._get_metadata_direct_device(video_url)
                if metadata:
                    return metadata
            
            metadata = VideoProbeUtil._get_metadata_ffmpeg(video_url)
            return metadata
        
        except Exception as e:
            logging.error(f"🚨 [APP] Error probing video {video_url}: {e}", exc_info=True)
            return None

    @staticmethod
    def _get_metadata_opencv(video_url: str) -> dict:
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            logging.warning(f"⚠️ [APP] OpenCV failed to open video: {video_url}")
            return None

        # Read first frame to ensure the video is valid
        ret, frame = cap.read()
        if not ret or frame is None:
            logging.warning(f"⚠️ [APP] OpenCV failed to read a frame from {video_url}")
            cap.release()
            return None

        height, width = frame.shape[:2]
        frame_rate = round(cap.get(cv2.CAP_PROP_FPS), 2)
        cap.release()
        
        return {
            "resolution": f"{width}x{height}" if width and height else None,
            "frame_rate": frame_rate if frame_rate > 0 else None,
            "timestamp": None
        }
    
    @staticmethod
    def _get_metadata_opencv_direct_device(device_idx: int) -> dict:
        """Fallback method to get metadata directly from camera device using OpenCV."""
        try:
            logging.debug(f"Attempting direct OpenCV access to device {device_idx}")
            cap = cv2.VideoCapture(device_idx)
            
            if not cap.isOpened():
                logging.warning(f"⚠️ [APP] OpenCV failed to open device {device_idx}")
                return None

            # Set a reasonable timeout and try to read a frame
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to get fresh frames
            
            # Try multiple attempts to read a frame (some cameras need warm-up)
            ret, frame = False, None
            for attempt in range(3):
                ret, frame = cap.read()
                if ret and frame is not None:
                    break
                logging.debug(f"Attempt {attempt + 1} failed to read frame from device {device_idx}")
            
            if not ret or frame is None:
                logging.warning(f"⚠️ [APP] OpenCV failed to read frame from device {device_idx} after 3 attempts")
                cap.release()
                return None

            # Get video properties
            height, width = frame.shape[:2]
            frame_rate = cap.get(cv2.CAP_PROP_FPS)
            
            # Some cameras report 0 FPS, use a reasonable default
            if frame_rate <= 0:
                frame_rate = 30.0
            else:
                frame_rate = round(frame_rate, 2)
            
            cap.release()
            
            logging.info(f"✅ [APP] Successfully probed device {device_idx} directly: {width}x{height} @ {frame_rate}fps")
            
            return {
                "resolution": f"{width}x{height}",
                "frame_rate": frame_rate,
                "timestamp": None
            }
            
        except Exception as e:
            logging.error(f"❌ [APP] Error probing device {device_idx} with OpenCV: {e}")
            return None
    
    @staticmethod
    def _get_metadata_ffmpeg_direct_device(device_idx: int) -> dict:
        """Fallback method to get metadata from camera device using FFmpeg."""
        if not shutil.which("ffprobe"):
            logging.warning("⚠️ [APP] ffprobe not available for device probing")
            return None
            
        try:
            system = platform.system().lower()
            
            # Determine the device input format based on OS
            if system == "linux":
                device_path = f"/dev/video{device_idx}"
                input_format = "v4l2"
                cmd = ["ffprobe", "-f", input_format, "-i", device_path]
            elif system == "windows":
                # Windows DirectShow device
                input_format = "dshow"
                device_name = f"video={device_idx}"  # This might need adjustment based on actual device names
                cmd = ["ffprobe", "-f", input_format, "-i", device_name]
            elif system == "darwin":  # macOS
                input_format = "avfoundation"
                cmd = ["ffprobe", "-f", input_format, "-i", str(device_idx)]
            else:
                logging.warning(f"⚠️ [APP] Unsupported platform for FFmpeg device access: {system}")
                return None
            
            # Add common ffprobe arguments
            cmd.extend([
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,avg_frame_rate",
                "-of", "json"
            ])
            
            logging.debug(f"Running FFmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logging.warning(f"⚠️ [APP] FFmpeg failed for device {device_idx}: {result.stderr.strip()}")
                return None
                
            if not result.stdout.strip():
                logging.warning(f"⚠️ [APP] No output from FFmpeg for device {device_idx}")
                return None

            metadata = json.loads(result.stdout)
            streams = metadata.get("streams", [])
            
            if not streams:
                logging.warning(f"⚠️ [APP] No video streams found for device {device_idx}")
                return None
                
            stream = streams[0]
            width = stream.get("width")
            height = stream.get("height")
            avg_fps = stream.get("avg_frame_rate", "30/1")

            try:
                frame_rate = round(float(fractions.Fraction(avg_fps)), 2)
            except (ValueError, ZeroDivisionError):
                frame_rate = 30.0

            if not width or not height:
                logging.warning(f"⚠️ [APP] Invalid resolution from FFmpeg for device {device_idx}")
                return None

            logging.info(f"✅ [APP] Successfully probed device {device_idx} with FFmpeg: {width}x{height} @ {frame_rate}fps")
            
            return {
                "resolution": f"{width}x{height}",
                "frame_rate": frame_rate,
                "timestamp": None
            }

        except subprocess.TimeoutExpired:
            logging.warning(f"⚠️ [APP] FFmpeg timeout for device {device_idx}")
        except json.JSONDecodeError:
            logging.error(f"❌ [APP] Failed to parse FFmpeg output for device {device_idx}")
        except Exception as e:
            logging.error(f"❌ [APP] Error probing device {device_idx} with FFmpeg: {e}")
            
        return None
    
    @staticmethod
    def _get_metadata_direct_device(device_index: str) -> dict:
        try:
            device_idx = int(device_index)
            
            logging.debug(f"VideoSharingClient available: {VideoSharingClient is not None}")
            
            # Try to use VideoSharingClient first for cross-process access
            if VideoSharingClient:
                try:
                    logging.debug("Attempting to use VideoSharingClient...")
                    
                    # Get storage path from DatabaseManager
                    storage_path = None
                    if get_storage_path:
                        try:
                            storage_path = str(get_storage_path())
                            logging.debug(f"Got storage path: {storage_path}")
                        except Exception as e:
                            logging.debug(f"Could not get storage path: {e}")
                    
                    # Create temporary client to get device properties
                    video_client = VideoSharingClient(device_idx, storage_path=storage_path)
                    logging.debug(f"Created VideoSharingClient, info_file: {video_client.info_file}")
                    
                    # Load daemon info to get properties without connecting
                    if video_client._load_daemon_info():
                        width = video_client.width
                        height = video_client.height
                        fps = video_client.fps
                        
                        return {
                            "resolution": f"{width}x{height}",
                            "frame_rate": round(fps, 2) if fps > 0 else 30.0,
                            "timestamp": None
                        }
                    else:
                        logging.debug(f"Video sharing daemon not available for device {device_idx}")
                    
                except Exception as e:
                    logging.debug(f"Video sharing not available for device {device_idx}: {e}")
                    import traceback
                    logging.debug(traceback.format_exc())
            
            # Fallback 1: Try direct OpenCV access
            logging.info(f"🔄 [APP] Daemon not available for device {device_idx}, falling back to direct OpenCV access")
            metadata = VideoProbeUtil._get_metadata_opencv_direct_device(device_idx)
            if metadata:
                return metadata
            
            # Fallback 2: Try FFmpeg for device access (Linux v4l2, Windows dshow)
            logging.info(f"🔄 [APP] OpenCV failed for device {device_idx}, trying FFmpeg device access")
            return VideoProbeUtil._get_metadata_ffmpeg_direct_device(device_idx)
            
        except Exception as e:
            logging.error(f"❌ [APP] Error getting metadata from direct device {device_index}: {e}")
            return None
    
    @staticmethod
    def _detect_stream_type(video_url: str) -> str:
        if hasattr(video_url, '__str__'):
            video_url = str(video_url)
        
        if isinstance(video_url, str) and video_url.isdigit():
            return "direct"
        
        parsed_url = urlparse(video_url)
        if parsed_url.scheme == "rtsp":
            return "rtsp"
        elif parsed_url.scheme in ["http", "https"]:
            return "http"
        else:
            return "file"
    
    @staticmethod
    def _get_metadata_ffmpeg(video_url: str) -> dict:
        if not shutil.which("ffprobe"):
            logging.error("⚠️ [APP] ffprobe is not installed or not found in PATH.")
            return None

        stream_type = VideoProbeUtil._detect_stream_type(video_url)
        
        if stream_type == "direct":
            return VideoProbeUtil._get_metadata_direct_device(video_url)
        
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", 
               "-show_entries", "stream=width,height,avg_frame_rate", "-of", "json"]
        
        if stream_type == "rtsp":
            probe_options = get_rtsp_probe_options()
            # Insert options at the beginning (after ffprobe)
            for i, option in enumerate(probe_options):
                cmd.insert(1 + i, option)
        
        cmd.append(video_url)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0 or not result.stdout.strip():
                logging.warning(f"⚠️ [APP] ffprobe failed for {video_url}: {result.stderr.strip()}")
                return None

            metadata = json.loads(result.stdout)
            streams = metadata.get("streams", [{}])[0]

            width = streams.get("width")
            height = streams.get("height")
            avg_fps = streams.get("avg_frame_rate", "0/1")

            try:
                frame_rate = round(float(fractions.Fraction(avg_fps)), 2)
            except (ValueError, ZeroDivisionError):
                frame_rate = None

            return {
                "resolution": f"{width}x{height}" if width and height else None,
                "frame_rate": frame_rate,
                "timestamp": None
            }

        except subprocess.TimeoutExpired:
            logging.warning(f"⚠️ [APP] ffprobe timeout for {video_url}")
        except json.JSONDecodeError:
            logging.error(f"❌ [APP] Failed to parse ffprobe output for {video_url}")

        return None