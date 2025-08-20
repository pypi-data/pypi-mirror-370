import logging
import re
import uuid
import grpc
from ..config.ConfigurationManager import ConfigurationManager
from ..util.PlatformDetector import PlatformDetector
from ..util.Networking import Networking
from ..services.ConnectionInfoClient import ConnectionInfoClient
from ..database.DatabaseManager import DatabaseManager


class AppInitializer:
    @staticmethod
    def validate_uuid(value):
        """Validate if the provided value is a valid UUID."""
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            raise ValueError(f"Invalid device ID format: {value}. Must be a valid UUID.")

    @staticmethod
    def validate_server_host(value):
        """Validate if the server host is a valid domain name or IP address."""
        domain_regex = (
            r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
            r"([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
        )
        ip_regex = (
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        if re.match(domain_regex, value) or re.match(ip_regex, value):
            return value
        raise ValueError(f"Invalid server host: {value}. Must be a valid domain or IP address.")

    @staticmethod
    def initialize_configuration(device_id: str, server_host: str, token: str):
        """
        Initialize the application configuration using the provided token
        and saving configuration data locally.
        """
        try:
            # Validate inputs
            AppInitializer.validate_uuid(device_id)
            AppInitializer.validate_server_host(server_host)

            # Get connection info using the ConnectionInfoClient
            connection_client = ConnectionInfoClient(server_host, 50051, token)
            connection_result = connection_client.get_connection_info()

            if not connection_result["success"]:
                logging.error(f"Device connection info failed: {connection_result['message']}")
                return

            worker_id = connection_result.get('id')
            if not worker_id:
                raise ValueError("No worker_id returned from connection info!")

            ConfigurationManager.set_config_batch({
                "worker_id": worker_id,
                "server_host": server_host,
                "token": token,
                "rabbitmq_host": connection_result['rabbitmq_host'],
                "rabbitmq_port": str(connection_result['rabbitmq_port']),
                "rabbitmq_username": connection_result['rabbitmq_username'],
                "rabbitmq_password": connection_result['rabbitmq_password']
            })
            ConfigurationManager.print_config()
        
        except ValueError as ve:
            logging.error(f"Validation error: {ve}")
        except grpc.RpcError as ge:
            logging.error(f"Grpc Error: {ge}")
        except Exception as e:
            logging.error(f"Unexpected error during initialization: {e}")
