import subprocess
import logging
import time
import platform
import threading
import numpy as np
import cv2
import os
from .VideoSharingDaemon import VideoSharingClient
from ..database.DatabaseManager import get_storage_path


class DirectDeviceToRTMPStreamer:
    def __init__(self, device_url: str, rtmp_server: str, stream_key: str, stream_duration: int):
        """
        Initialize the DirectDeviceToRTMPStreamer.
        
        Args:
            device_url: Camera device URL or index (as string)
            rtmp_server: RTMP server base URL
            stream_key: Stream key/UUID
            stream_duration: Duration in seconds
        """
        self.device_url = device_url
        self.rtmp_server = rtmp_server
        self.stream_key = stream_key
        self.duration = stream_duration
        
        # Parse device index from URL
        is_device, device_index = self._is_direct_device(device_url)
        if not is_device:
            raise ValueError(f"Invalid device URL: {device_url}")
        
        self.device_index = device_index
        self.rtmp_url = f"{rtmp_server}/{stream_key}"
        
        self.ffmpeg_process = None
        self.active = False
        self.stop_event = threading.Event()
        
        # Streaming state variables
        self.started = False
        self.start_time = None
        self.width = None
        self.height = None
        self.fps = 30  # Default FPS
        self.bitrate = "2000k"  # Default bitrate
        
        # Video sharing components
        self.video_client = None

    def _calculate_resolution(self, frame):
        """Determines resolution with max width 1024 while maintaining aspect ratio."""
        original_height, original_width = frame.shape[:2]
        if original_width > 1024:
            scale_factor = 1024 / original_width
            new_width = 1024
            new_height = int(original_height * scale_factor)
        else:
            new_width, new_height = original_width, original_height

        logging.info(f"📏 [APP] Adjusted resolution: {new_width}x{new_height} (Original: {original_width}x{original_height})")
        return new_width, new_height

    def is_active(self):
        """Check if the RTMP streamer is active and ready to send frames."""
        return self.active and self.ffmpeg_process and self.ffmpeg_process.poll() is None

    def _start_ffmpeg_stream(self):
        """Starts an FFmpeg process to stream frames to the RTMP server silently."""
        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-loglevel", "warning",  # Show warnings and errors
            "-nostats",             # Hide encoding progress updates
            "-hide_banner",         # Hide FFmpeg banner information
            "-f", "rawvideo",
            "-pixel_format", "bgr24",
            "-video_size", f"{self.width}x{self.height}",
            "-framerate", str(self.fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-b:v", self.bitrate,
            # Disable Audio (Avoid unnecessary encoding overhead)
            "-an",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-f", "flv",
            # Remove duration limit - let application control duration
            self.rtmp_url,
        ]

        try:
            with open(os.devnull, "w") as devnull:
                self.ffmpeg_process = subprocess.Popen(
                    ffmpeg_command,
                    stdin=subprocess.PIPE,
                    stdout=devnull,
                    stderr=subprocess.PIPE  # Capture stderr for error monitoring
                )
            logging.info(f"📡 [APP] RTMP streaming started: {self.rtmp_url} ({self.width}x{self.height})")
            self.started = True
            self.active = True
            
            # Start error monitoring thread
            error_thread = threading.Thread(target=self._monitor_ffmpeg_stderr, daemon=True)
            error_thread.start()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ [APP] Failed to start FFmpeg: {e}")
            self.ffmpeg_process = None
            self.active = False
            return False

    def send_frame(self, frame):
        """Sends a video frame to the RTMP stream with dynamic resolution."""
        if frame is None or not isinstance(frame, np.ndarray):
            logging.error("❌ [APP] Invalid frame received")
            return

        try:
            # Check if duration has been exceeded
            if self.start_time and time.time() - self.start_time > self.duration:
                logging.info("🕒 [APP] Stream duration reached, stopping")
                self.stop_stream()
                return

            # Validate frame before processing
            if frame.size == 0 or not frame.data:
                logging.error("❌ [APP] Empty frame detected")
                return

            # Set resolution on the first frame
            if not self.started:
                self.width, self.height = self._calculate_resolution(frame)
                if not self._start_ffmpeg_stream():
                    logging.error("❌ [APP] Failed to start FFmpeg stream")
                    return

            if self.is_active():
                # Create a copy of the frame to prevent reference issues
                frame_copy = frame.copy()
                
                # Resize only if necessary
                if frame_copy.shape[1] > 1024:
                    frame_copy = cv2.resize(frame_copy, (self.width, self.height), 
                                         interpolation=cv2.INTER_AREA)

                # Additional frame validation
                if frame_copy.size == 0 or not frame_copy.data:
                    logging.error("❌ [APP] Frame became invalid after processing")
                    return

                if self.ffmpeg_process and self.ffmpeg_process.stdin:
                    self.ffmpeg_process.stdin.write(frame_copy.tobytes())
                    # Don't flush - let FFmpeg handle buffering

        except BrokenPipeError:
            logging.error("❌ [APP] RTMP connection broken")
            self.stop_stream()
        except Exception as e:
            logging.error(f"❌ [APP] Failed to send frame to RTMP: {e}")
            self.stop_stream()

    def _monitor_ffmpeg_stderr(self):
        """Monitor FFmpeg stderr for errors and important messages."""
        if not self.ffmpeg_process or not self.ffmpeg_process.stderr:
            return
            
        try:
            while self.ffmpeg_process.poll() is None and not self.stop_event.is_set():
                line = self.ffmpeg_process.stderr.readline()
                if line:
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    if line_str:
                        # Filter important messages
                        if any(keyword in line_str.lower() for keyword in ['error', 'failed', 'invalid', 'could not']):
                            logging.error(f"🚨 [FFmpeg] {line_str}")
                        elif any(keyword in line_str.lower() for keyword in ['warning', 'deprecated']):
                            logging.warning(f"⚠️ [FFmpeg] {line_str}")
                        else:
                            logging.debug(f"ℹ️ [FFmpeg] {line_str}")
        except Exception as e:
            logging.warning(f"Error monitoring FFmpeg stderr: {e}")

    def _is_direct_device(self, url) -> bool:
        """Check if the URL is a direct video device."""
        try:
            device_index = int(url)
            return True, device_index
        except ValueError:
            return False, None

    def start_stream(self):
        """Start streaming direct device to RTMP using cross-process video sharing with fallbacks."""
        is_device, device_index = self._is_direct_device(self.device_url)
        if not is_device:
            logging.error(f"❌ [APP] Invalid direct device URL: {self.device_url}")
            return

        self.device_index = device_index
        
        logging.info(f"🔄 [APP] Attempting video sharing daemon for device {self.device_index}")
        if self._try_video_sharing_daemon():
            return
        
        # Fallback 1: Direct OpenCV streaming
        logging.info(f"🔄 [APP] Video sharing daemon not available for device {self.device_index}, falling back to direct OpenCV streaming")
        if self._start_direct_opencv_streaming():
            return
            
        # Fallback 2: Direct FFmpeg streaming
        logging.info(f"🔄 [APP] OpenCV streaming failed for device {self.device_index}, trying direct FFmpeg streaming")
        if self._start_direct_ffmpeg_streaming():
            return
            
        logging.error(f"❌ [APP] All streaming methods failed for device {self.device_index}")

    def _try_video_sharing_daemon(self):
        """Try to start streaming using video sharing daemon with timeout."""
        try:
            # Get storage path from DatabaseManager
            storage_path = None
            if get_storage_path:
                try:
                    storage_path = str(get_storage_path())
                except Exception as e:
                    logging.debug(f"Could not get storage path from DatabaseManager: {e}")
            
            # Create video sharing client
            self.video_client = VideoSharingClient(self.device_index, storage_path=storage_path)
            
            # Check if daemon info file exists and is valid (quick check, no long wait)
            max_wait_time = 5  # Reduced wait time for daemon check
            wait_interval = 1   # Check every 1 second
            wait_elapsed = 0
            
            logging.debug(f"🔄 [APP] Quick check for video sharing daemon for device {self.device_index}...")
            
            while wait_elapsed < max_wait_time:
                if self.video_client._load_daemon_info():
                    logging.info(f"✅ [APP] Found video sharing daemon for device {self.device_index}")
                    break
                
                logging.debug(f"⏳ [APP] Checking for daemon... ({wait_elapsed}/{max_wait_time}s)")
                time.sleep(wait_interval)
                wait_elapsed += wait_interval
            else:
                # Timeout reached - daemon not available
                logging.debug(f"⚠️ [APP] Video sharing daemon not available for device {self.device_index} within {max_wait_time}s")
                return False
            
            # Connect to the video sharing daemon
            if not self.video_client.connect(self._on_frame_received):
                logging.error(f"❌ [APP] Failed to connect to video sharing daemon for device {self.device_index}")
                return False
            
            # Get device properties
            width, height, fps, pixel_format = self.video_client.get_device_properties()
            self.fps = fps if fps > 0 else 30
            
            logging.info(f"📡 [APP] Starting cross-process device to RTMP stream: {self.device_url} → {self.rtmp_url} for {self.duration} seconds")
            logging.info(f"📹 [APP] Device properties: {width}x{height} @ {fps}fps")
            
            # Record start time for duration tracking
            self.start_time = time.time()
            
            logging.info(f"✅ [APP] Cross-process device streaming configured successfully")
            return True

        except Exception as e:
            logging.debug(f"🚨 [APP] Error starting cross-process device stream: {e}")
            return False

    def _start_direct_opencv_streaming(self):
        """Start streaming using direct OpenCV access to the camera device."""
        try:
            logging.info(f"🎥 [APP] Starting direct OpenCV streaming for device {self.device_index}")
            
            # Open camera with OpenCV
            cap = cv2.VideoCapture(self.device_index)
            if not cap.isOpened():
                logging.error(f"❌ [APP] Failed to open device {self.device_index} with OpenCV")
                return False
            
            # Set buffer size to reduce latency
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Get camera properties
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            self.fps = original_fps if original_fps > 0 else 30
            
            # Test reading a frame to ensure camera works
            ret, test_frame = cap.read()
            if not ret or test_frame is None:
                logging.error(f"❌ [APP] Failed to read test frame from device {self.device_index}")
                cap.release()
                return False
            
            # Set resolution based on first frame
            self.width, self.height = self._calculate_resolution(test_frame)
            
            # Start FFmpeg process
            if not self._start_ffmpeg_stream():
                cap.release()
                return False
            
            logging.info(f"✅ [APP] Direct OpenCV streaming started: {self.width}x{self.height} @ {self.fps}fps")
            
            # Record start time for duration tracking
            self.start_time = time.time()
            self.active = True
            
            # Start streaming thread
            streaming_thread = threading.Thread(target=self._opencv_streaming_loop, args=(cap,), daemon=True)
            streaming_thread.start()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ [APP] Error in direct OpenCV streaming: {e}", exc_info=True)
            return False

    def _opencv_streaming_loop(self, cap):
        """Main loop for OpenCV streaming."""
        try:
            frame_interval = 1.0 / self.fps
            last_frame_time = 0
            
            while self.active and not self.stop_event.is_set():
                current_time = time.time()
                
                # Check duration limit
                if self.start_time and (current_time - self.start_time) >= self.duration:
                    logging.info(f"⏰ [APP] Stream duration reached ({self.duration}s), stopping...")
                    break
                
                # Frame rate control
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.001)  # Small sleep to prevent busy waiting
                    continue
                
                ret, frame = cap.read()
                if not ret or frame is None:
                    logging.warning(f"⚠️ [APP] Failed to read frame from device {self.device_index}")
                    time.sleep(0.1)  # Wait before retrying
                    continue
                
                # Process and send frame
                self._process_and_send_frame(frame)
                last_frame_time = current_time
            
        except Exception as e:
            logging.error(f"❌ [APP] Error in OpenCV streaming loop: {e}", exc_info=True)
        finally:
            cap.release()
            self.stop_stream()

    def _process_and_send_frame(self, frame):
        """Process and send frame to RTMP stream."""
        try:
            if not self.is_active():
                return
            
            # Resize frame if necessary
            if frame.shape[1] > 1024:
                frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
            
            # Send frame to FFmpeg
            if self.ffmpeg_process and self.ffmpeg_process.stdin:
                self.ffmpeg_process.stdin.write(frame.tobytes())
                
        except BrokenPipeError:
            logging.error("❌ [APP] RTMP connection broken")
            self.stop_stream()
        except Exception as e:
            logging.error(f"❌ [APP] Failed to send frame to RTMP: {e}")
            self.stop_stream()

    def _start_direct_ffmpeg_streaming(self):
        """Start streaming using direct FFmpeg access to the camera device."""
        try:
            logging.info(f"🎥 [APP] Starting direct FFmpeg streaming for device {self.device_index}")
            
            # Determine platform-specific input format
            system = platform.system().lower()
            if system == "linux":
                input_format = "v4l2"
                device_path = f"/dev/video{self.device_index}"
            elif system == "windows":
                input_format = "dshow"
                device_path = f"video={self.device_index}"
            elif system == "darwin":  # macOS
                input_format = "avfoundation"
                device_path = str(self.device_index)
            else:
                logging.error(f"❌ [APP] Unsupported platform for direct FFmpeg streaming: {system}")
                return False
            
            # Set default properties
            self.width = 1024  # Will be adjusted by FFmpeg
            self.height = 768
            self.fps = 30
            
            # Build FFmpeg command for direct device streaming
            ffmpeg_command = [
                "ffmpeg",
                "-y",
                "-loglevel", "warning",
                "-nostats",
                "-hide_banner",
                "-f", input_format,
                "-i", device_path,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-tune", "zerolatency",
                "-b:v", self.bitrate,
                "-an",  # No audio
                "-maxrate", "2500k",
                "-bufsize", "5000k",
                "-f", "flv"
            ]
            
            # Add duration limit if specified
            if self.duration > 0:
                ffmpeg_command.extend(["-t", str(self.duration)])
            
            ffmpeg_command.append(self.rtmp_url)
            
            logging.debug(f"FFmpeg command: {' '.join(ffmpeg_command)}")
            
            # Start FFmpeg process
            with open(os.devnull, "w") as devnull:
                self.ffmpeg_process = subprocess.Popen(
                    ffmpeg_command,
                    stdout=devnull,
                    stderr=subprocess.PIPE
                )
            
            # Check if process started successfully
            time.sleep(1)  # Give FFmpeg time to initialize
            if self.ffmpeg_process.poll() is not None:
                # Process has already terminated
                stderr_output = self.ffmpeg_process.stderr.read().decode('utf-8', errors='ignore')
                logging.error(f"❌ [APP] FFmpeg process failed to start: {stderr_output}")
                return False
            
            self.active = True
            self.start_time = time.time()
            
            # Start stderr monitoring
            stderr_thread = threading.Thread(target=self._monitor_ffmpeg_stderr, daemon=True)
            stderr_thread.start()
            
            # Start duration monitoring
            duration_thread = threading.Thread(target=self._monitor_duration, daemon=True)
            duration_thread.start()
            
            logging.info(f"✅ [APP] Direct FFmpeg streaming started for device {self.device_index}")
            return True
            
        except Exception as e:
            logging.error(f"❌ [APP] Error in direct FFmpeg streaming: {e}", exc_info=True)
            return False

    def _monitor_duration(self):
        """Monitor streaming duration and stop when limit is reached."""
        try:
            while self.active and not self.stop_event.is_set():
                if self.start_time and (time.time() - self.start_time) >= self.duration:
                    logging.info(f"⏰ [APP] Stream duration reached ({self.duration}s), stopping...")
                    self.stop_stream()
                    break
                time.sleep(1)
        except Exception as e:
            logging.error(f"❌ [APP] Error monitoring duration: {e}")

    def _on_frame_received(self, frame, timestamp=None):
        """Callback when frame is received from video sharing daemon."""
        try:
            # Send frame directly to RTMP
            self.send_frame(frame)
        except Exception as e:
            logging.warning(f"Error processing frame: {e}")
    
    def _cleanup_on_error(self):
        """Clean up resources on error."""
        try:
            if self.video_client:
                self.video_client.disconnect()
                self.video_client = None
        except Exception as e:
            logging.warning(f"Error during cleanup: {e}")

    def stop_stream(self):
        """Stops the FFmpeg streaming process and disconnects from video sharing."""
        logging.info(f"🛑 [APP] Stopping device stream")
        
        self.active = False
        self.stop_event.set()
        
        if self.ffmpeg_process:
            try:
                if self.ffmpeg_process.stdin:
                    self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except Exception as e:
                logging.error(f"❌ [APP] Error stopping RTMP stream: {e}")
                # Force kill if normal termination fails
                try:
                    self.ffmpeg_process.kill()
                except Exception:
                    pass
            finally:
                self.ffmpeg_process = None
                logging.info("✅ [APP] RTMP streaming process stopped.")
        
        # Disconnect from video sharing
        if self.video_client:
            try:
                self.video_client.disconnect()
                self.video_client = None
                logging.info(f"🔓 [APP] Disconnected from video sharing daemon")
            except Exception as e:
                logging.warning(f"⚠️ [APP] Error disconnecting from video sharing: {e}")

    def is_running(self):
        """Check if the streaming process is running."""
        return self.is_active()
