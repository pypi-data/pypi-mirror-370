import threading
import time
import logging
from ..services.AIModelClient import AIModelClient
from ..services.WorkerSourceClient import WorkerSourceClient
from ..services.WorkerSourcePipelineClient import WorkerSourcePipelineClient
from ..services.GrpcClientBase import GrpcClientBase

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

logger = logging.getLogger(__name__)

class DataSyncWorker:
    def __init__(self, config: dict, sync_interval=10):
        """
        Initializes the Data Sync Worker.

        Args:
            config (dict): Configuration dictionary.
            sync_interval (int): Interval (in seconds) for synchronization.
        """
        if not isinstance(config, dict):
            raise ValueError("⚠️ [APP] config must be a dictionary.")

        self.config = config
        self.worker_id = self.config.get("worker_id")
        self.server_host = self.config.get("server_host")
        self.token = self.config.get("token")

        if not self.worker_id:
            raise ValueError("⚠️ [APP] Configuration is missing 'worker_id'.")
        if not self.server_host:
            raise ValueError("⚠️ [APP] Configuration is missing 'server_host'.")
        if not self.token:
            raise ValueError("⚠️ [APP] Configuration is missing 'token'.")

        self.ai_model_client = AIModelClient(self.token, self.server_host)
        self.worker_source_client = WorkerSourceClient(self.server_host)
        self.worker_source_pipeline_client = WorkerSourcePipelineClient(self.server_host)

        self.sync_interval = sync_interval
        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def start(self):
        """Start the data synchronization worker thread."""
        with self.lock:
            if self.thread and self.thread.is_alive():
                logger.warning("⚠️ [APP] Sync Worker is already running.")
                return

            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"🚀 [APP] Sync Worker started (Device: {self.worker_id}).")

    def stop(self):
        """Stop the data sync worker."""
        logging.info("🛑 [DATA SYNC] Stopping DataSyncWorker.")
        self.running = False
        self.ai_model_client.cleanup_downloads()
        safe_join_thread(self.thread)
        logging.info("🛑 [DATA SYNC] DataSyncWorker stopped.")

    def _run(self):
        """Main loop for syncing worker sources and pipelines."""
        try:
            while not self.stop_event.is_set():
                self._sync_ai_models()
                self._sync_worker_sources()
                self._sync_worker_source_pipelines()
                self._sync_worker_source_pipelines_debug()
                self._sync_worker_source_pipelines_detection()
                time.sleep(self.sync_interval)
        except Exception as e:
            logger.error("🚨 [APP] Unexpected error in Sync Worker main loop.", exc_info=True)

    def _sync_ai_models(self):
        """Synchronize worker sources from the server."""
        try:
            response = self.ai_model_client.sync_ai_models(self.worker_id)
            
            if not response or not response.get("success"):
                error_message = GrpcClientBase.get_error_message(response)
                logger.error(f"❌ [APP] Failed to sync AI Models: {error_message}")

        except Exception as e:
            logger.error("🚨 [APP] Error syncing AI Models.", exc_info=True)

    def _sync_worker_sources(self):
        """Synchronize worker sources from the server."""
        try:
            response = self.worker_source_client.sync_worker_sources(self.worker_id, self.token)
            
            if not response or not response.get("success"):
                error_message = GrpcClientBase.get_error_message(response)
                logger.error(f"❌ [APP] Failed to sync worker sources: {error_message}")

        except Exception as e:
            logger.error("🚨 [APP] Error syncing worker sources.", exc_info=True)


    def _sync_worker_source_pipelines(self):
        """Synchronize worker source pipelines from the server."""
        try:
            response = self.worker_source_pipeline_client.get_worker_source_pipeline_list(self.worker_id, self.token)

            if not response or not response.get("success"):
                error_message = GrpcClientBase.get_error_message(response)
                logger.error(f"❌ [APP] Failed to sync worker source pipelines: {error_message}")

        except Exception as e:
            logger.error("🚨 [APP] Error syncing worker source pipelines.", exc_info=True)

    def _sync_worker_source_pipelines_debug(self):
        """Synchronize worker source pipelines debug with the server."""
        try:
            response = self.worker_source_pipeline_client.sync_pipeline_debug(self.token)

            if not response or not response.get("success"):
                error_message = GrpcClientBase.get_error_message(response)
                logger.error(f"❌ [APP] Failed to sync restricted area violations: {error_message}")

        except Exception as e:
            logger.error("🚨 [APP] Error syncing worker source pipelines debug.", exc_info=True)


    def _sync_worker_source_pipelines_detection(self):
        """Synchronize worker source pipelines detection with the server."""
        try:
            response = self.worker_source_pipeline_client.sync_pipeline_detection(self.token)

            if not response or not response.get("success"):
                error_message = GrpcClientBase.get_error_message(response)
                logger.error(f"❌ [APP] Failed to sync dataset sources: {error_message}")

        except Exception as e:
            logger.error("🚨 [APP] Error syncing worker source pipelines detection.", exc_info=True)