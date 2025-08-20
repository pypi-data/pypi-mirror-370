import time
import multiprocessing
import signal
import sys
import logging

try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    pass

from .initializer.AppInitializer import AppInitializer
from .worker.WorkerManager import WorkerManager
from .config.ConfigurationManager import ConfigurationManager
from .util.HardwareID import HardwareID
from .services.GrpcClientBase import set_auth_failure_callback
from .database.DatabaseManager import set_storage_path
from . import models


class WorkerService:
    """
    Main worker service class that manages the worker agent lifecycle.
    Uses hardware ID-based authentication and configuration management.
    """
    
    def __init__(
        self,
        server_host: str = "be.vision.sindika.co.id",
        token: str = None,
        system_usage_interval: int = 30,
        rtmp_server: str = "rtmp://live.vision.sindika.co.id:1935/live",
        storage_path: str = "data",
        server_port: int = 50051,
    ):
        """
        Initialize the worker service.
        
        Args:
            server_host: Manager server host (default: 'be.vision.sindika.co.id')
            token: Authentication token for the worker (obtained from frontend)
            system_usage_interval: Interval for system usage reporting (default: 30)
            rtmp_server: RTMP server URL for video streaming
            storage_path: Storage path for databases and files (default: 'data')
            server_port: gRPC server port (default: 50051)
        """
        # Set the global storage path before any database operations
        set_storage_path(storage_path)
        
        self.logger = self._setup_logging()
        self.worker_manager = None
        self.running = False
        self.server_host = server_host
        self.token = token
        self.system_usage_interval = system_usage_interval
        self.rtmp_server = rtmp_server
        self.storage_path = storage_path
        self.server_port = server_port
        self.config = None
        self.auth_failure_detected = False
        
        # Register authentication failure callback
        set_auth_failure_callback(self._on_authentication_failure)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _on_authentication_failure(self):
        """Called when an authentication failure is detected."""
        if not self.auth_failure_detected:
            self.auth_failure_detected = True
            self.logger.error("🔑 [APP] Authentication failure detected. Shutting down service...")
            self.stop()

    def _setup_logging(self):
        """Configure logging settings (allows inline emojis)."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # Only show warnings and errors
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("pika").setLevel(logging.WARNING)
        logging.getLogger("grpc").setLevel(logging.FATAL)
        logging.getLogger("ffmpeg").setLevel(logging.FATAL)
        logging.getLogger("subprocess").setLevel(logging.FATAL)
        
        return logging.getLogger(__name__)

    def _initialize_configuration(self):
        """Initialize the application configuration."""
        self.logger.info("🚀 [APP] Initializing application...")

        # Initialize database
        ConfigurationManager.init_database()

        # Load all configurations at once
        config = ConfigurationManager.get_all_configs()
        
        # Use the server_host parameter directly
        server_host = self.server_host
        self.logger.info(f"🌐 [APP] Using server host: {server_host}")

        # Check if configuration exists
        if not config:
            self.logger.info("⚙️ [APP] Configuration not found. Performing first-time setup...")

            # Get hardware ID
            hardware_id = HardwareID.get_unique_id()

            self.logger.info(f"🖥️ [APP] Detected Hardware ID: {hardware_id}")
            self.logger.info(f"🌐 [APP] Using Server Host: {server_host}")

            # Check if token is provided
            if not self.token:
                raise ValueError("Token is required for worker initialization. Please provide a token obtained from the frontend.")

            # Initialize with token
            AppInitializer.initialize_configuration(hardware_id, server_host, self.token)

            # Set server_port in config for first-time setup
            ConfigurationManager.set_config("server_port", str(self.server_port))

            # Get configuration
            config = ConfigurationManager.get_all_configs()
        else:
            # Check if server_host, server_port, or token has changed and update if needed
            config_updated = False
            
            if config['server_host'] != server_host:
                ConfigurationManager.set_config("server_host", server_host)
                config_updated = True
                self.logger.info(f"✅ [APP] Updated server host to: {server_host}")
            
            # Check if server_port has changed and update if needed
            if str(config.get('server_port')) != str(self.server_port):
                ConfigurationManager.set_config("server_port", str(self.server_port))
                config_updated = True
                self.logger.info(f"✅ [APP] Updated server port to: {self.server_port}")
            
            # Check if token has changed and update if needed
            if self.token and config.get('token') != self.token:
                ConfigurationManager.set_config("token", self.token)
                config_updated = True
                self.logger.info("✅ [APP] Updated authentication token")
            
            if config_updated:
                config = ConfigurationManager.get_all_configs()
                self.logger.info("✅ [APP] Configuration updated successfully")
            else:
                self.logger.info("✅ [APP] Configuration found. No changes needed.")
        
        # Add runtime parameters to config
        config['rtmp_server'] = self.rtmp_server
        
        return config

    def initialize(self) -> bool:
        """
        Initialize the worker service components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Worker service initialization started")
            
            # Initialize configuration
            self.config = self._initialize_configuration()
            
            if not self.config:
                raise RuntimeError("Failed to initialize configuration")

            # Initialize WorkerManager
            self.worker_manager = WorkerManager(self.config)

            self.logger.info("Worker service initialization completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize worker service: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def start(self):
        """Start the worker service"""
        if not self.running:
            self.running = True
            self.logger.info("Worker service started")
            try:
                # Start all workers via WorkerManager
                self.worker_manager.start_all()
                # Block main thread to keep process alive
                while self.running and not self.auth_failure_detected:
                    time.sleep(1)
                
                # If authentication failure was detected, exit with error code
                if self.auth_failure_detected:
                    self.logger.error("🔑 [APP] Service terminated due to authentication failure")
                    sys.exit(1)
            except Exception as e:
                self.logger.error(f"Error in worker service: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
                self.stop()
        else:
            self.logger.info("Service already running.")
    
    def stop(self):
        """Stop the worker service"""
        if self.running:
            self.running = False
            self.logger.info("Worker service stopping...")
            try:
                # Stop all workers via WorkerManager
                if hasattr(self, 'worker_manager'):
                    self.worker_manager.stop_all()
                self.logger.info("Worker service stopped")
            except Exception as e:
                self.logger.error(f"Error stopping worker service: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
        else:
            self.logger.info("Service already stopped.")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def run(self):
        """Run the worker service"""
        if self.initialize():
            self.start()
        else:
            self.logger.error("Failed to initialize worker service")
            sys.exit(1)


def main():
    """Main entry point for the worker service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nedo Vision Worker Service")
    parser.add_argument(
        "--server-host", 
        default="be.vision.sindika.co.id",
        help="Manager server host (default: be.vision.sindika.co.id)"
    )
    parser.add_argument(
        "--server-port",
        type=int,
        default=50051,
        help="gRPC server port (default: 50051)"
    )
    parser.add_argument(
        "--system-usage-interval",
        type=int,
        default=30,
        help="System usage reporting interval in seconds (default: 30)"
    )
    args = parser.parse_args()
    
    # Create and run worker service
    service = WorkerService(
        server_host=args.server_host,
        server_port=args.server_port,
        system_usage_interval=args.system_usage_interval
    )
    service.run()


if __name__ == "__main__":
    main()