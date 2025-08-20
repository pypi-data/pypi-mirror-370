import threading
import logging
import json
from .RabbitMQListener import RabbitMQListener

logger = logging.getLogger(__name__)

def safe_join_thread(thread, timeout=5):
    """Safely join a thread, avoiding RuntimeError when joining current thread."""
    if thread and thread != threading.current_thread():
        thread.join(timeout=timeout)
    elif thread == threading.current_thread():
        logging.info("🛑 [APP] Thread stopping from within itself, skipping join.")

class CoreActionWorker:
    def __init__(self, config: dict, start_cb, stop_cb):
        """
        Initialize Core Action Worker.

        Args:
            config (dict): Configuration object containing settings.
            start_cb: Callback function to start the worker.
            stop_cb: Callback function to stop the worker.
        """
        if not isinstance(config, dict):
            raise ValueError("⚠️ [APP] config must be a dictionary.")

        self.config = config
        self.worker_id = self.config.get("worker_id")
        self.start_cb = start_cb
        self.stop_cb = stop_cb

        if not self.worker_id:
            raise ValueError("⚠️ [APP] Configuration is missing 'worker_id'.")

        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        # Initialize RabbitMQ listener
        self.listener = RabbitMQListener(
            self.config, self.worker_id, self.stop_event, self._process_core_action_message
        )

    def start(self):
        """Start the Core Action Worker."""
        with self.lock:
            if self.thread and self.thread.is_alive():
                logger.warning("⚠️ [APP] Core Action Worker is already running.")
                return

            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"🚀 [APP] Core Action Worker started (Device: {self.worker_id}).")

    def stop(self):
        """Stop the Core Action Worker."""
        with self.lock:
            if not self.thread or not self.thread.is_alive():
                logger.warning("⚠️ [APP] Core Action Worker is not running.")
                return

            self.stop_event.set()
            self.listener.stop_listening()

            safe_join_thread(self.thread)
            self.thread = None
            logger.info(f"🛑 [APP] Core Action Worker stopped (Device: {self.worker_id}).")

    def _run(self):
        """Main loop to manage RabbitMQ listener."""
        try:
            while not self.stop_event.is_set():
                logger.info("📡 [APP] Starting core action message listener...")
                self.listener.start_listening(
                    exchange_name="nedo.worker.core.action", 
                    queue_name=f"nedo.worker.core.{self.worker_id}"
                )
                
                # Wait for the listener thread to finish (connection lost or stop requested)
                while not self.stop_event.is_set() and self.listener.listener_thread and self.listener.listener_thread.is_alive():
                    self.listener.listener_thread.join(timeout=5)  # Check every 5 seconds
                
                if not self.stop_event.is_set():
                    logger.warning("⚠️ [APP] Core action listener disconnected. Attempting to reconnect in 10 seconds...")
                    self.stop_event.wait(10)  # Wait 10 seconds before reconnecting
                else:
                    logger.info("📡 [APP] Core action listener stopped.")
                    break
                    
        except Exception as e:
            logger.error("🚨 [APP] Unexpected error in Core Action Worker loop.", exc_info=True)

    def _process_core_action_message(self, message):
        """
        Process received core action messages.
        
        Args:
            message (str): JSON message containing action and timestamp
        """
        try:
            data = json.loads(message)
            action = data.get('action')
            timestamp = data.get('timestamp')

            logger.info(f"📥 [APP] Received core action: {action} at {timestamp}")

            if action == "start":
                logger.info(f"🚀 [APP] Starting processing workers")
                self.start_cb()
                logger.info(f"✅ [APP] Started processing workers")
                
            elif action == "stop":
                logger.info(f"🛑 [APP] Stopping processing workers")
                self.stop_cb()
                logger.info(f"✅ [APP] Stopped processing workers")
                
            elif action == "restart":
                logger.info(f"🔄 [APP] Restarting processing workers")
                self.start_cb()
                self.stop_cb()
                logger.info(f"✅ [APP] Restarted processing workers")
                
            elif action == "debug":
                # TODO: do something on debugging, not now
                logger.info(f"🔍 [APP] Debugging")
                
            else:
                logger.warning(f"⚠️ [APP] Unknown core action received: {action}")

        except json.JSONDecodeError:
            logger.error("🚨 [APP] Failed to parse core action message JSON")
        except Exception as e:
            logger.error(f"🚨 [APP] Error processing core action: {str(e)}")

