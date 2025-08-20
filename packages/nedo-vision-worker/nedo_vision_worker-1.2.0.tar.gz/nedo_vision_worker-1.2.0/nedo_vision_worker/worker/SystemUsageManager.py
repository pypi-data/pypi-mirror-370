import logging
import threading
import time
from ..util.SystemMonitor import SystemMonitor
from ..services.SystemUsageClient import SystemUsageClient
from ..services.GrpcClientBase import GrpcClientBase
from ..util.Networking import Networking 

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class SystemUsageManager:
    def __init__(self, server_host: str, device_id: str, token: str):
        """
        Handles system usage monitoring, latency tracking, and reporting.

        Args:
            server_host (str): The gRPC server host.
            device_id (str): Unique ID of the device (passed externally).
            token (str): Authentication token for the worker.
        """
        if not device_id:
            raise ValueError("⚠️ [APP] 'device_id' cannot be empty.")
        if not token:
            raise ValueError("⚠️ [APP] 'token' cannot be empty.")

        self.system_monitor = SystemMonitor()
        self.system_usage_client = SystemUsageClient(server_host)
        self.server_host = server_host
        self.device_id = device_id
        self.token = token
        self.latency = None
        self.latency_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.latency_thread = None  

        self._start_latency_monitoring()

    def _start_latency_monitoring(self):
        """Starts a background thread to monitor network latency."""
        if self.latency_thread and self.latency_thread.is_alive():
            logger.warning("⚠️ [APP] Latency monitoring thread is already running.")
            return

        self.latency_thread = threading.Thread(target=self._monitor_latency, daemon=True)
        self.latency_thread.start()
        logger.info("📡 [APP] Latency monitoring started.")

    def _monitor_latency(self):
        """Periodically checks the network latency using gRPC and updates the latency variable."""
        server_port = 50051  # Default gRPC port

        while not self.stop_event.is_set():
            try:
                latency_value = Networking.check_grpc_latency(self.server_host, server_port)
                with self.latency_lock:
                    self.latency = latency_value
                # logger.info(f"🔄 [APP] Updated network latency: {latency_value} ms")

            except Exception as e:
                logger.error("🚨 [APP] Error checking gRPC latency.", exc_info=True)
                with self.latency_lock:
                    self.latency = None  
            time.sleep(10) 

    def process_system_usage(self):
        """Collect and send system usage data to the server, including network latency."""
        try:
            usage = self.system_monitor.get_system_usage()
            cpu_usage = usage["cpu"]["usage_percent"]
            ram_usage = usage["ram"]
            gpu_usage = usage.get("gpu", [])

            with self.latency_lock:
                latency = self.latency if self.latency is not None else -1

            response = self.system_usage_client.send_system_usage(
                device_id=self.device_id,
                cpu_usage=cpu_usage,
                ram_usage=ram_usage,
                gpu_usage=gpu_usage,
                latency=latency,
                token=self.token,
            )

            if not response or not response.get("success"):
                error_message = GrpcClientBase.get_error_message(response)
                logger.error(f"❌ [APP] Failed to send system usage: {error_message}")
            #else:
            #    logger.info("✅ [APP] System usage sent successfully.")

        except Exception as e:
            logger.error("🚨 [APP] Error sending system usage.", exc_info=True)

    def close(self):
        """Closes the system usage client and stops the latency thread."""
        self.stop_event.set()

        if self.latency_thread and self.latency_thread.is_alive():
            safe_join_thread(self.latency_thread)
            logger.info("🔌 [APP] Latency monitoring thread stopped.")

        if self.system_usage_client:
            self.system_usage_client.close_client()
            logger.info("✅ [APP] SystemUsageClient closed.")
