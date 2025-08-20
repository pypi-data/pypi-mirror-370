import requests
import socket
import logging
import time
import grpc
from ..protos.VisionWorkerService_pb2_grpc import HealthCheckServiceStub
from ..protos.VisionWorkerService_pb2 import HealthCheckRequest



class Networking:

    @staticmethod
    def check_grpc_latency(server_host: str, server_port: int = 50051) -> float:
        try:
            channel = grpc.insecure_channel(f"{server_host}:{server_port}")
            stub = HealthCheckServiceStub(channel)
            request = HealthCheckRequest()

            start_time = time.time()
            response = stub.HealthCheck(request)
            end_time = time.time()

            latency = (end_time - start_time) * 1000
            return latency

        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return -1

    @staticmethod
    def check_latency(server_url: str) -> float:
        """
        Measures the latency to the specified server URL.

        Args:
            server_url (str): The URL of the server to check latency for.

        Returns:
            float: The latency in milliseconds.
        """
        import time

        try:
            start_time = time.time()  # Record the start time
            response = requests.get(server_url)  # Send the GET request
            end_time = time.time()  # Record the end time

            if response.status_code == 200:
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                return latency
            else:
                raise Exception(f"Server responded with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error occurred while checking latency: {e}")

    @staticmethod
    def get_public_ip() -> str:
        """
        Gets the current public IP address.

        Returns:
            str: The public IP address as a string.
        """
        try:
            response = requests.get("https://api.ipify.org?format=json")
            if response.status_code == 200:
                return response.json().get("ip", "Unable to retrieve IP address")
            else:
                raise Exception(f"Failed to get public IP. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error occurred while retrieving public IP: {e}")

    @staticmethod
    def get_local_ip() -> str:
        """
        Gets the local IP address assigned to the system's network interface.

        Returns:
            str: The local IP address (not loopback), or a fallback message if not connected.
        """
        try:
            # Create a temporary socket to determine the local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # Connect to a public IP (Google's DNS server) on port 80
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]  # Retrieve the local IP address
            return local_ip
        except OSError as e:
            # Handle network unreachable or other OS-related errors
            logging.warning(f"Could not determine local IP address: {e}")
            return "127.0.0.1"


