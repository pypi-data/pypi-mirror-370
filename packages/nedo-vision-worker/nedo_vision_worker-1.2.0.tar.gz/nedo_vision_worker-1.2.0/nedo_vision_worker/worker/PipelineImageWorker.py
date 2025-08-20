import threading
import logging
import json
from ..repositories.WorkerSourceRepository import WorkerSourceRepository
from ..services.WorkerSourcePipelineClient import WorkerSourcePipelineClient
from .RabbitMQListener import RabbitMQListener

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class PipelineImageWorker:
    def __init__(self, config: dict):
        """
        Initialize Pipeline Image Worker.

        Args:
            config (dict): Configuration object containing settings.
        """
        if not isinstance(config, dict):
            raise ValueError("⚠️ [APP] config must be a dictionary.")

        self.config = config
        self.worker_id = self.config.get("worker_id")
        self.server_host = self.config.get("server_host")
        self.token = self.config.get("token")

        if not self.worker_id:
            raise ValueError("⚠️ [APP] Configuration is missing 'worker_id'.")
        if not self.token:
            raise ValueError("⚠️ [APP] Configuration is missing 'token'.")
        
        self.worker_source_pipeline_client = WorkerSourcePipelineClient(self.server_host)

        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        self.worker_source_repo = WorkerSourceRepository()

        # Initialize RabbitMQ listener
        self.listener = RabbitMQListener(
            self.config, self.worker_id, self.stop_event, self._process_image_request_message
        )

    def start(self):
        """Start the Pipeline Image Worker."""
        with self.lock:
            if self.thread and self.thread.is_alive():
                logger.warning("⚠️ [APP] Pipeline Image Worker is already running.")
                return

            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)  # ✅ Run as daemon
            self.thread.start()
            logger.info(f"🚀 [APP] Pipeline Image Worker started (Device: {self.worker_id}).")

    def stop(self):
        """Stop the Pipeline Image Worker."""
        with self.lock:
            if not self.thread or not self.thread.is_alive():
                logger.warning("⚠️ [APP] Pipeline Image Worker is not running.")
                return

            self.stop_event.set()
            self.listener.stop_listening()

            safe_join_thread(self.thread)  # Ensures the thread stops gracefully
            self.thread = None
            logger.info(f"🛑 [APP] Pipeline Image Worker stopped (Device: {self.worker_id}).")

    def _run(self):
        """Main loop to manage RabbitMQ listener."""
        try:
            while not self.stop_event.is_set():
                logger.info("📡 [APP] Starting image request message listener...")
                self.listener.start_listening(exchange_name="nedo.pipeline.image.request", queue_name=f"nedo.pipeline.request.{self.worker_id}")
                
                # Wait for the listener thread to finish (connection lost or stop requested)
                while not self.stop_event.is_set() and self.listener.listener_thread and self.listener.listener_thread.is_alive():
                    self.listener.listener_thread.join(timeout=5)  # Check every 5 seconds
                
                if not self.stop_event.is_set():
                    logger.warning("⚠️ [APP] Image request listener disconnected. Attempting to reconnect in 10 seconds...")
                    self.stop_event.wait(10)  # Wait 10 seconds before reconnecting
                else:
                    logger.info("📡 [APP] Image request listener stopped.")
                    break
                    
        except Exception as e:
            logger.error("🚨 [APP] Unexpected error in Pipeline Image Worker loop.", exc_info=True)

    def _process_image_request_message(self, message):
        """Process messages related to video preview streaming."""
        try:
            data = json.loads(message)
            worker_source_pipeline_id = data.get("workerSourcePipelineId")
            worker_source_id = data.get("workerSourceId")
            uuid = data.get("uuid")

            worker_source = self.worker_source_repo.get_worker_source_by_id(worker_source_id)
            if not worker_source:
                return
            
            logger.info(f"📡 [APP] Sending Pipeline Image Preview to Worker Source Pipeline: {worker_source_pipeline_id}")
            
            response = self.worker_source_pipeline_client.send_pipeline_image(
                worker_source_pipeline_id=worker_source_pipeline_id,
                uuid=uuid,
                url=worker_source.url if worker_source.type_code in ["live", "direct"] else worker_source.file_path,
                token=self.token
            )

            if response.get("success"):
                logger.info("✅ [APP] Successfully sent Pipeline Image Preview.")
            else:
                logger.error(f"❌ [APP] Failed to send Pipeline Image Preview: {response.get('message')}")

        except json.JSONDecodeError:
            logger.error("⚠️ [APP] Invalid JSON message format.")
        except Exception as e:
            logger.error("🚨 [APP] Error processing video preview message.", exc_info=True)
