import logging
import threading
import time

from ..repositories.RestrictedAreaRepository import RestrictedAreaRepository
from ..services.RestrictedAreaClient import RestrictedAreaClient

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class RestrictedAreaManager:
    def __init__(self, server_host: str, worker_id: str, worker_source_id: str, token: str):
        """
        Handles restricted area violation monitoring and reporting.

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

        self.client = RestrictedAreaClient(server_host)
        self.server_host = server_host
        self.worker_id = worker_id
        self.worker_source_id = worker_source_id
        self.token = token
        self.violations_data = []
        self.stop_event = threading.Event()
        self.violation_thread = None
        self.repo = RestrictedAreaRepository()

        self._start_violation_monitoring()

    def _start_violation_monitoring(self):
        """Starts a background thread to monitor and collect restricted area violations."""
        if self.violation_thread and self.violation_thread.is_alive():
            logger.warning("⚠️ [APP] Restricted area violation thread already running.")
            return

        logger.info("📡 [APP] Restricted area violation monitoring started.")

    def send_violation_batch(self):
        """Sends a batch of collected violation data to the server."""
        try:
            self.violations_data = self.repo.get_latest_5_violations()
            if not self.violations_data:
                return

            response = self.client.send_upsert_batch(
                worker_id=self.worker_id,
                worker_source_id=self.worker_source_id,
                violation_data=self.violations_data,
                token=self.token
            )

            if response.get("success"):
                logger.info("✅ [APP] Successfully sent restricted area violation batch.")
                self.violations_data.clear()
            else:
                logger.error(f"❌ [APP] Failed to send restricted area violation batch: {response.get('message')}")

        except Exception as e:
            logger.error("🚨 [APP] Error sending restricted area violation batch.", exc_info=True)

    def close(self):
        """Closes the violation client and stops the monitoring thread."""
        self.stop_event.set()

        if self.violation_thread and self.violation_thread.is_alive():
            safe_join_thread(self.violation_thread)
            logger.info("🔌 [APP] Restricted area violation monitoring thread stopped.")

        if self.client:
            logger.info("✅ [APP] Restricted Area Violation Client closed.")
