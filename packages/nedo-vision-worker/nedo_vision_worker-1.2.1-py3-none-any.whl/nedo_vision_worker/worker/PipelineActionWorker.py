import threading
import logging
import json
from ..repositories.WorkerSourcePipelineDebugRepository import WorkerSourcePipelineDebugRepository
from ..repositories.WorkerSourcePipelineRepository import WorkerSourcePipelineRepository
from .RabbitMQListener import RabbitMQListener

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class PipelineActionWorker:
    def __init__(self, config: dict):
        """
        Initialize Pipeline Action Worker.

        Args:
            config (dict): Configuration object containing settings.
        """
        if not isinstance(config, dict):
            raise ValueError("⚠️ [APP] config must be a dictionary.")

        self.config = config
        self.worker_id = self.config.get("worker_id")

        if not self.worker_id:
            raise ValueError("⚠️ [APP] Configuration is missing 'worker_id'.")

        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        self.repo = WorkerSourcePipelineRepository()
        self.debug_repo = WorkerSourcePipelineDebugRepository()

        # Initialize RabbitMQ listener
        self.listener = RabbitMQListener(
            self.config, self.worker_id, self.stop_event, self._process_pipeline_action_message
        )

    def start(self):
        """Start the Pipeline Action Worker."""
        with self.lock:
            if self.thread and self.thread.is_alive():
                logger.warning("⚠️ [APP] Pipeline Action Worker is already running.")
                return

            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"🚀 [APP] Pipeline Action Worker started (Device: {self.worker_id}).")

    def stop(self):
        """Stop the Pipeline Action Worker."""
        with self.lock:
            if not self.thread or not self.thread.is_alive():
                logger.warning("⚠️ [APP] Pipeline Action Worker is not running.")
                return

            self.stop_event.set()
            self.listener.stop_listening()

            safe_join_thread(self.thread)
            self.thread = None
            logger.info(f"🛑 [APP] Pipeline Action Worker stopped (Device: {self.worker_id}).")

    def _run(self):
        """Main loop to manage RabbitMQ listener."""
        try:
            while not self.stop_event.is_set():
                logger.info("📡 [APP] Starting pipeline action message listener...")
                self.listener.start_listening(
                    exchange_name="nedo.worker.pipeline.action", 
                    queue_name=f"nedo.worker.pipeline.{self.worker_id}"
                )
                
                # Wait for the listener thread to finish (connection lost or stop requested)
                while not self.stop_event.is_set() and self.listener.listener_thread and self.listener.listener_thread.is_alive():
                    self.listener.listener_thread.join(timeout=5)  # Check every 5 seconds
                
                if not self.stop_event.is_set():
                    logger.warning("⚠️ [APP] Pipeline action listener disconnected. Attempting to reconnect in 10 seconds...")
                    self.stop_event.wait(10)  # Wait 10 seconds before reconnecting
                else:
                    logger.info("📡 [APP] Pipeline action listener stopped.")
                    break
                    
        except Exception as e:
            logger.error("🚨 [APP] Unexpected error in Pipeline Action Worker loop.", exc_info=True)

    def _process_pipeline_action_message(self, message):
        """
        Process received Pipeline action messages.
        
        Args:
            message (str): JSON message containing action and timestamp
        """
        try:
            data = json.loads(message)
            uuid = data.get('uuid')
            pipeline_id = data.get('workerSourcePipelineId')
            action = data.get('action')
            timestamp = data.get('timestamp')

            logger.info(f"📥 [APP] Received Pipeline action: {pipeline_id}:{action} at {timestamp}")

            pipeline = self.repo.get_worker_source_pipeline(pipeline_id)

            if not pipeline:
                logger.warning(f"⚠️ [APP] Pipeline not found: {pipeline_id}")
                return

            if action == "start":
                pipeline.pipeline_status_code = "run"
                
            elif action == "stop":
                pipeline.pipeline_status_code = "stop"
                
            elif action == "restart":
                pipeline.pipeline_status_code = "restart"
                
            elif action == "debug":
                self.debug_repo.create_debug_entry(uuid, pipeline_id)
                
            else:
                logger.warning(f"⚠️ [APP] Unknown Pipeline action received: {action}")

            self.repo.session.commit()
            logger.info(f"✅ [APP] Pipeline action processed: {pipeline_id}:{action}")

        except json.JSONDecodeError:
            logger.error("🚨 [APP] Failed to parse Pipeline action message JSON")
        except Exception as e:
            logger.error(f"🚨 [APP] Error processing Pipeline action: {str(e)}")

