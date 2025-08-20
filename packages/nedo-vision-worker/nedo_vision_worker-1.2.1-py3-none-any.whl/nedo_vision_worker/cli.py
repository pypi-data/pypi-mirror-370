import argparse
import signal
import sys
import traceback
import logging
from typing import NoReturn

from .worker_service import WorkerService


class NedoWorkerCLI:
    """Main CLI application for Nedo Vision Worker Service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame) -> NoReturn:
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Nedo Vision Worker Service",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Check system dependencies and requirements
  nedo-worker doctor

  # Start worker service
  nedo-worker run --token your-token-here

  # Start with custom configuration
  nedo-worker run --token your-token-here \\
    --rtmp-server rtmp://custom.server.com:1935/live \\
    --server-host custom.server.com \\
    --storage-path /custom/storage/path
            """
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version="nedo-vision-worker 1.2.1"
        )
        
        subparsers = parser.add_subparsers(
            dest='command', 
            help='Available commands',
            required=True
        )
        
        self._add_doctor_command(subparsers)
        self._add_run_command(subparsers)
        
        return parser
    
    def _add_doctor_command(self, subparsers) -> None:
        """Add the doctor command."""
        subparsers.add_parser(
            'doctor',
            help='Check system dependencies and requirements',
            description='Run diagnostic checks for FFmpeg, OpenCV, gRPC and other dependencies'
        )
    
    def _add_run_command(self, subparsers) -> None:
        """Add the run command with its arguments."""
        run_parser = subparsers.add_parser(
            'run',
            help='Start the worker service',
            description='Start the Nedo Vision Worker Service'
        )
        
        run_parser.add_argument(
            "--token",
            required=True,
            help="Authentication token for the worker (obtained from frontend)"
        )
        
        run_parser.add_argument(
            "--server-host",
            default="be.vision.sindika.co.id",
            help="Server hostname for communication (default: %(default)s)"
        )
        
        run_parser.add_argument(
            "--server-port",
            type=int,
            default=50051,
            help="Server port for gRPC communication (default: %(default)s)"
        )
        
        run_parser.add_argument(
            "--rtmp-server",
            default="rtmp://live.vision.sindika.co.id:1935/live",
            help="RTMP server URL for video streaming (default: %(default)s)"
        )
        
        run_parser.add_argument(
            "--storage-path",
            default="data",
            help="Storage path for databases and files (default: %(default)s)"
        )
        
        run_parser.add_argument(
            "--system-usage-interval",
            type=int,
            default=30,
            metavar="SECONDS",
            help="System usage reporting interval in seconds (default: %(default)s)"
        )
        
        run_parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default="INFO",
            help="Set the logging level (default: %(default)s)"
        )
    
    def run_doctor_command(self) -> int:
        """Execute the doctor command."""
        try:
            from .doctor import main as doctor_main
            return doctor_main()
        except ImportError as e:
            self.logger.error(f"Failed to import doctor module: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"Doctor command failed: {e}")
            return 1
    
    def run_worker_service(self, args: argparse.Namespace) -> int:
        """Start and run the worker service."""
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, args.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        try:
            # Create the worker service
            service = WorkerService(
                server_host=args.server_host,
                token=args.token,
                system_usage_interval=args.system_usage_interval,
                rtmp_server=args.rtmp_server,
                storage_path=args.storage_path,
                server_port=args.server_port
            )
            
            # Log startup information
            self._log_startup_info(args)
            
            # Start the service
            service.run()
            
            # Keep the service running
            self._wait_for_service(service)
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
            return 0
        except Exception as e:
            self.logger.error(f"Service failed: {e}")
            if args.log_level == "DEBUG":
                traceback.print_exc()
            return 1
    
    def _log_startup_info(self, args: argparse.Namespace) -> None:
        """Log service startup information."""
        self.logger.info("🚀 Starting Nedo Vision Worker Service...")
        self.logger.info(f"🌐 Server: {args.server_host}")
        self.logger.info(f"🔑 Token: {args.token[:8]}{'*' * (len(args.token) - 8)}")
        self.logger.info(f"⏱️  System Usage Interval: {args.system_usage_interval}s")
        self.logger.info(f"📡 RTMP Server: {args.rtmp_server}")
        self.logger.info(f"💾 Storage Path: {args.storage_path}")
        self.logger.info("Press Ctrl+C to stop the service")
    
    def _wait_for_service(self, service: WorkerService) -> None:
        """Wait for the service to run and handle shutdown."""
        import time
        
        try:
            while getattr(service, 'running', False):
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested...")
        finally:
            if hasattr(service, 'stop'):
                service.stop()
            self.logger.info("✅ Service stopped successfully")
    
    def run(self) -> int:
        """Main entry point for the CLI application."""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if args.command == 'doctor':
            return self.run_doctor_command()
        elif args.command == 'run':
            return self.run_worker_service(args)
        else:
            parser.print_help()
            return 1


def main() -> int:
    """Main CLI entry point."""
    cli = NedoWorkerCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())