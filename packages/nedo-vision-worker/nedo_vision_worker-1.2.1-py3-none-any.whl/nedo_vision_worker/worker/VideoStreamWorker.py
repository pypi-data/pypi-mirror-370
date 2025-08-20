import os
import threading
import logging
import json
from ..database.DatabaseManager import get_storage_path
from ..services.FileToRTMPServer import FileToRTMPStreamer
from ..services.DirectDeviceToRTMPStreamer import DirectDeviceToRTMPStreamer
from ..services.SharedDirectDeviceClient import SharedDirectDeviceClient
from .RabbitMQListener import RabbitMQListener
from ..services.RTSPtoRTMPStreamer import RTSPtoRTMPStreamer

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class VideoStreamWorker:
    def __init__(self, config: dict, stream_duration=300):
        """
        Initialize Video Stream Worker.

        Args:
            config (dict): Configuration object containing settings.
            stream_duration (int): Default stream duration in seconds.
        """
        if not isinstance(config, dict):
            raise ValueError("⚠️ [APP] config must be a dictionary.")

        self.config = config
        self.worker_id = self.config.get("worker_id")
        self.source_file_path = get_storage_path("files") / "source_files"

        if not self.worker_id:
            raise ValueError("⚠️ [APP] Configuration is missing 'worker_id'.")

        self.stream_duration = stream_duration
        self.rtmp_server = self.config.get("rtmp_server")
        
        if not self.rtmp_server:
            raise ValueError("⚠️ [APP] RTMP server URL is required but not provided in configuration.")

        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Initialize shared device client for direct video devices
        self.shared_device_client = SharedDirectDeviceClient()

        # Initialize RabbitMQ listener
        self.listener = RabbitMQListener(
            self.config, self.worker_id, self.stop_event, self._process_video_preview_message
        )

    def start(self):
        """Start the Video Stream Worker."""
        with self.lock:
            if self.thread and self.thread.is_alive():
                logger.warning("⚠️ [APP] Stream Worker is already running.")
                return

            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)  # ✅ Run as daemon
            self.thread.start()
            logger.info(f"🚀 [APP] Stream Worker started (Device: {self.worker_id}).")

    def stop(self):
        """Stop the Video Stream Worker."""
        with self.lock:
            if not self.thread or not self.thread.is_alive():
                logger.warning("⚠️ [APP] Stream Worker is not running.")
                return

            self.stop_event.set()
            self.listener.stop_listening()

            safe_join_thread(self.thread)  # Ensures the thread stops gracefully
            self.thread = None
            logger.info(f"🛑 [APP] Stream Worker stopped (Device: {self.worker_id}).")
    
    def _is_direct_device(self, url) -> bool:
        """Check if the URL is a direct video device."""
        is_device, _ = self.shared_device_client._is_direct_device(url)
        return is_device

    def _run(self):
        """Main loop to manage RabbitMQ listener."""
        try:
            while not self.stop_event.is_set():
                logger.info("📡 [APP] Starting video stream message listener...")
                self.listener.start_listening(exchange_name="nedo.worker.stream.preview", queue_name=f"nedo.worker.preview.{self.worker_id}")
                
                # Wait for the listener thread to finish (connection lost or stop requested)
                while not self.stop_event.is_set() and self.listener.listener_thread and self.listener.listener_thread.is_alive():
                    self.listener.listener_thread.join(timeout=5)  # Check every 5 seconds
                
                if not self.stop_event.is_set():
                    logger.warning("⚠️ [APP] Video stream listener disconnected. Attempting to reconnect in 10 seconds...")
                    self.stop_event.wait(10)  # Wait 10 seconds before reconnecting
                else:
                    logger.info("📡 [APP] Video stream listener stopped.")
                    break
                    
        except Exception as e:
            logger.error("🚨 [APP] Unexpected error in Stream Worker loop.", exc_info=True)

    def _process_video_preview_message(self, message):
        """Process messages related to video preview streaming."""
        try:
            data = json.loads(message)
            worker_id = data.get("workerId")
            url = data.get("url")
            uuid = data.get("uuid")
            stream_duration = int(data.get("duration", self.stream_duration)) 

            logger.info(f"📡 [APP] Received video preview message ({data})")

            # Validate URL - support RTSP, worker-source files, and direct devices
            if not url:
                logger.error(f"⚠️ [APP] Missing URL in message")
                return
            
            is_valid_url = (
                url.startswith("rtsp://") or 
                url.startswith("worker-source/") or 
                self._is_direct_device(url)
            )
            
            if not is_valid_url:
                logger.error(f"⚠️ [APP] Invalid URL: {url} (must be RTSP, worker-source file, or direct device)")
                return

            if stream_duration <= 0:
                logger.warning(f"⚠️ [APP] Invalid stream duration {stream_duration}. Using default {self.stream_duration}s.")
                stream_duration = self.stream_duration

            logger.info(f"📡 [APP] Forwarding to RTMP (Worker: {worker_id}, UUID: {uuid})")

            # Start a streaming thread
            threading.Thread(
                target=self._start_stream,
                args=(url, self.rtmp_server, uuid, stream_duration, worker_id),
                daemon=True,
            ).start()

        except json.JSONDecodeError:
            logger.error("⚠️ [APP] Invalid JSON message format.")
        except Exception as e:
            logger.error("🚨 [APP] Error processing video preview message.", exc_info=True)

    def _start_stream(self, url, rtmp_server, stream_key, stream_duration, worker_id):
        """Runs streaming to RTMP in a separate thread."""
        try:
            logger.info(f"🎥 [APP] Starting RTMP stream (Worker: {worker_id})")
            
            if url.startswith("worker-source/"):
                streamer = FileToRTMPStreamer(self.source_file_path / os.path.basename(url), rtmp_server, stream_key, stream_duration)
            elif self._is_direct_device(url):
                streamer = DirectDeviceToRTMPStreamer(url, rtmp_server, stream_key, stream_duration)
            else:
                # Assume RTSP or other supported protocols
                streamer = RTSPtoRTMPStreamer(url, rtmp_server, stream_key, stream_duration)

            streamer.start_stream()

            # Schedule stream stop
            threading.Timer(stream_duration, streamer.stop_stream).start()
            logger.info(f"⏳ [APP] Stopping RTMP stream in {stream_duration}s.")

        except Exception as e:
            logger.error("🚨 [APP] Error in stream worker.", exc_info=True)
