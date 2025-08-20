import threading
import logging
import time
import pika
import pika.exceptions

logger = logging.getLogger(__name__)

class RabbitMQListener:
    def __init__(self, config, device_id, stop_event, message_callback):
        self.config = config
        self.device_id = device_id.lower()
        self.stop_event = stop_event
        self.message_callback = message_callback
        self.connection = None
        self.channel = None
        self.exchange_name = None
        self.queue_name = None
        self.listener_thread = None
        self.reconnect_delay = 5  # Exponential backoff (max 60s)

    def _connect(self):
        """Establish a new RabbitMQ connection."""
        rabbitmq_host = self.config.get("rabbitmq_host")
        rabbitmq_port = int(self.config.get("rabbitmq_port", 5672))
        rabbitmq_username = self.config.get("rabbitmq_username")
        rabbitmq_password = self.config.get("rabbitmq_password")

        credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            virtual_host='/',
            credentials=credentials,
            heartbeat=30,
            blocked_connection_timeout=10
        )

        try:
            self.connection = pika.SelectConnection(
                parameters,
                on_open_callback=self._on_connected,
                on_close_callback=self._on_closed
            )
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"⚠️ [APP] Connection failed: {e}")
            return False

        return True

    def _on_connected(self, connection):
        """Callback for successful RabbitMQ connection."""
        logger.info("🔌 [APP] Connected to RabbitMQ")
        self.connection = connection
        self.connection.channel(on_open_callback=self._on_channel_open)

    def _on_channel_open(self, channel):
        """Callback for successfully opened channel."""
        self.channel = channel
        routing_key = self.device_id

        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct', durable=True)
        self.channel.queue_declare(queue=self.queue_name, durable=False, auto_delete=True, exclusive=True)
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=routing_key)
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._on_message_received, auto_ack=True)

        logger.info(f"📡 [APP] Listening for RabbitMQ messages on '{self.exchange_name}' with routing key '{routing_key}'.")

    def _on_closed(self, connection, reason):
        """Handle unexpected connection closure."""
        logger.error(f"🚨 [APP] RabbitMQ connection closed unexpectedly: {reason}")
        self._cleanup_connection()
        time.sleep(self.reconnect_delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, 60)
        self.start_listening(self.exchange_name, self.queue_name)  # Restart listener

    def start_listening(self, exchange_name, queue_name):
        """
        Establish a RabbitMQ connection and listen for messages.
        Automatically reconnects if the connection is lost.
        """
        if not self.stop_event:
            logger.error("🚨 [APP] Stop event is not initialized")
            return

        self.exchange_name = exchange_name
        self.queue_name = queue_name

        if self.listener_thread and self.listener_thread.is_alive():
            logger.warning("⚠️ [APP] RabbitMQ listener is already running.")
            return
            
        # Clean up any dead thread reference
        if self.listener_thread and not self.listener_thread.is_alive():
            self.listener_thread = None

        def run():
            while not self.stop_event.is_set():
                if self._connect():
                    try:
                        self.connection.ioloop.start()  # Start pika's event loop
                    except KeyboardInterrupt:
                        self.stop_listening()
                        break
                    except Exception as e:
                        logger.error(f"🚨 [APP] Unexpected RabbitMQ error: {e}")
                        time.sleep(self.reconnect_delay)
                        self.reconnect_delay = min(self.reconnect_delay * 2, 60)
                else:
                    logger.error(f"⚠️ [APP] Connection failed. Retrying in {self.reconnect_delay}s...")
                    time.sleep(self.reconnect_delay)

        # Start RabbitMQ listener in a new thread
        self.listener_thread = threading.Thread(target=run, daemon=True)
        self.listener_thread.start()

    def stop_listening(self):
        """
        Stop RabbitMQ listening and close the connection.
        """
        logger.info("🛑 [APP] Stopping RabbitMQ listener...")
        if not self.stop_event:
            logger.error("🚨 [APP] Stop event is not initialized")
            return

        self.stop_event.set()

        try:
            if self.channel and self.channel.is_open:
                self.channel.close()

            if self.connection and self.connection.is_open:
                self.connection.close()

            if self.connection:
                self.connection.ioloop.stop()  # Stop pika event loop

        except Exception as e:
            logger.error(f"🚨 [APP] Error during RabbitMQ shutdown: {e}")

        self._cleanup_connection()
        
        # Clean up the listener thread reference
        if self.listener_thread:
            if self.listener_thread.is_alive():
                self.listener_thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish
            self.listener_thread = None
            
        logger.info("🔌 [APP] RabbitMQ listener stopped.")

    def _cleanup_connection(self):
        """Safely close RabbitMQ connection and channel."""
        if self.channel:
            try:
                if self.channel.is_open:
                    self.channel.close()
            except Exception:
                pass
            self.channel = None

        if self.connection:
            try:
                if self.connection.is_open:
                    self.connection.close()
                    self.connection.ioloop.stop()
            except Exception:
                pass
            self.connection = None

    def _on_message_received(self, ch, method, properties, body):
        """
        Callback function triggered when a message is received.
        """
        try:
            message = body.decode("utf-8")
            logger.info(f"📩 [APP] Received RabbitMQ message: {message}")
            self.message_callback(message)
        except Exception as e:
            logger.error(f"🚨 [APP] Error processing RabbitMQ message: {e}")
