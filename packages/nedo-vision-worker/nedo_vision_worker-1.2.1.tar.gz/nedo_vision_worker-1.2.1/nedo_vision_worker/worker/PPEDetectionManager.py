import logging
import threading
import time
from ..services.PPEDetectionClient import PPEDetectionClient
from ..repositories.PPEDetectionRepository import PPEDetectionRepository
from ..util.Networking import Networking

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class PPEDetectionManager:
    def __init__(self, server_host: str, worker_id: str, worker_source_id: str, token: str):
        """
        Handles PPE detection monitoring and reporting.

        Args:
            server_host (str): The gRPC server host.
            worker_id (str): Unique worker ID (passed externally).
            worker_source_id (str): Unique worker source ID (passed externally).
            token (str): Authentication token for the worker.
        """
        if not worker_id or not worker_source_id:
            raise ValueError("⚠️ [APP] 'worker_id' and 'worker_source_id' cannot be empty.")
        if not token:
            raise ValueError("⚠️ [APP] 'token' cannot be empty.")

        self.ppe_detection_client = PPEDetectionClient(server_host)
        self.server_host = server_host
        self.worker_id = worker_id
        self.worker_source_id = worker_source_id
        self.token = token
        self.ppe_detection_data = []
        self.stop_event = threading.Event()
        self.ppe_detection_thread = None
        self.ppe_detection_repo = PPEDetectionRepository()

        self._start_ppe_detection_monitoring()

    def _start_ppe_detection_monitoring(self):
        """Starts a background thread to monitor and collect PPE detection data."""
        if self.ppe_detection_thread and self.ppe_detection_thread.is_alive():
            logger.warning("⚠️ [APP] PPE detection monitoring thread is already running.")
            return

        logger.info("📡 [APP] PPE detection monitoring started.")


    def send_ppe_detection_batch(self):
        """Sends a batch of collected PPE detection data to the server."""
        try:
            self.ppe_detection_data = self.ppe_detection_repo.get_latest_5_detections()
            if not self.ppe_detection_data:
                return

            response = self.ppe_detection_client.send_upsert_batch(
                worker_id=self.worker_id,
                worker_source_id=self.worker_source_id,
                detection_data=self.ppe_detection_data,
                token=self.token
            )

            if response.get("success"):
                logger.info("✅ [APP] Successfully sent PPE detection batch.")
                self.ppe_detection_data.clear() 
            else:
                logger.error(f"❌ [APP] Failed to send PPE detection batch: {response.get('message')}")

        except Exception as e:
            logger.error("🚨 [APP] Error sending PPE detection batch.", exc_info=True)

    def close(self):
        """Closes the PPE detection client and stops the monitoring thread."""
        self.stop_event.set()

        if self.ppe_detection_thread and self.ppe_detection_thread.is_alive():
            safe_join_thread(self.ppe_detection_thread)
            logger.info("🔌 [APP] PPE detection monitoring thread stopped.")

        if self.ppe_detection_client:
            logger.info("✅ [APP] PPE Detection Client closed.")
